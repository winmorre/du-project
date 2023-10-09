import logging
import typing
from logging.handlers import WatchedFileHandler
from os import makedirs
from pathlib import Path

import structlog
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter as HttpMetricExporter
from opentelemetry.instrumentation import requests, fastapi, sqlalchemy,psycopg2
from opentelemetry.metrics import get_meter_provider, set_meter_provider, CallbackOptions, Observation
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader, ConsoleMetricExporter
from opentelemetry.sdk.metrics.view import SumAggregation, View
from opentelemetry.sdk.trace import ReadableSpan, TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, SpanExportResult, SimpleSpanProcessor, SpanExporter

_Logger = structlog.getLogger(__name__)


class AppLogSpanExporter(SpanExporter):
    def __init__(self, logger):
        self.logger = logger

    def export(self, spans: typing.Sequence[ReadableSpan]) -> SpanExportResult:
        for span in spans:
            self.logger.debug(span.to_json(indent=4))

        return SpanExportResult.SUCCESS


def tracing_configuration(trace_log_file_path: typing.Optional[str],
                          jaeger_params: typing.Optional[typing.Dict[str, typing.Any]], app):
    requests.RequestsInstrumentor().instrument()
    fastapi_instrumentor = fastapi.FastAPIInstrumentor()
    fastapi_instrumentor.instrument()
    fastapi_instrumentor.instrument_app(app=app)
    psycopg2.Psycopg2Instrumentor().instrument()
    # redis.RedisInstrumentor().instrument()
    sqlalchemy.SQLAlchemyInstrumentor().instrument()
    # mysql_instrumentor = mysql.MySQLInstrumentor()
    # mysql_instrumentor.instrument()
    # mysql_instrumentor.instrument_connection(connection=mysql_connection)
    # grpc.GrpcInstrumentorServer().instrument()
    # grpc.GrpcAioInstrumentorServer().instrument()
    # grpc.GrpcAioInstrumentorClient().instrument()
    # grpc.GrpcInstrumentorClient().instrument()

    tracer_provider: TracerProvider = trace.get_tracer_provider()

    if trace_log_file_path:
        log_dir = Path(trace_log_file_path).parent
        makedirs(log_dir, exist_ok=True)
        trace_logger = logging.getLogger("app_trace_exporter")
        trace_logger.setLevel(logging.DEBUG)
        trace_logger.propagate = False
        handler = WatchedFileHandler(trace_log_file_path)
        handler.setLevel(logging.DEBUG)
        trace_logger.addHandler(handler)

        trace_exporter = AppLogSpanExporter(trace_logger)
        tracer_provider.add_span_processor(SimpleSpanProcessor(trace_exporter))

    if jaeger_params:
        jaeger_exporter = JaegerExporter(**jaeger_params)
        tracer_provider.add_span_processor(BatchSpanProcessor(jaeger_exporter))


def metrics_configurations():
    hist_to_sum_view = View(instrument_name="http.client.request.latency", aggregation=SumAggregation())

    #  for local development, use the console exporter
    exporter = ConsoleMetricExporter()

    # create a metric reader with stdout exporter
    reader = PeriodicExportingMetricReader(exporter, export_interval_millis=1_000)
    provider = MeterProvider(
        metric_readers=[reader],
        views=[hist_to_sum_view],
    )

    set_meter_provider(provider)
    meter = get_meter_provider().get_meter("view-change-aggregation", "0.1.2")
    histogram = meter.create_histogram("http.client.request.latency")

    return histogram


def observable_counter_func(options: CallbackOptions) -> typing.Iterable[Observation]:
    yield Observation(1, {})


def observable_up_down_counter_func(options: CallbackOptions) -> typing.Iterable[Observation]:
    yield Observation(-10, {})


def observable_gauge_func(options: CallbackOptions) -> typing.Iterable[Observation]:
    yield Observation(9, {})


def alt_metrics_configuration():
    grpc_exporter = OTLPMetricExporter(insecure=True)
    http_exporter = HttpMetricExporter()

    grpc_reader = PeriodicExportingMetricReader(exporter=grpc_exporter, export_interval_millis=5_000)
    http_reader = PeriodicExportingMetricReader(exporter=http_exporter, export_interval_millis=5_000)

    provider = MeterProvider(metric_readers=[grpc_reader, http_reader])

    set_meter_provider(provider)

    meter = get_meter_provider().get_meter("app-metrics", version="0.1.0")

    # Counter
    counter = meter.create_counter("counter")
    counter.add(1)

    # Async counter
    observable_counter = meter.create_observable_counter("observable_counter", [observable_counter_func])

    # upDownCounter
    updown_counter = meter.create_up_down_counter("updown_counter")
    updown_counter.add(1)
    updown_counter.add(-5)

    # Async UpDownCounter
    observable_updown_counter = meter.create_observable_up_down_counter(
        "observable_updown_counter", [observable_up_down_counter_func]
    )

    # Histogram
    histogram = meter.create_histogram("histogram")
    histogram.record(99.9)

    # Async Gauge
    gauge = meter.create_observable_gauge("gauge", [observable_gauge_func])

    return counter, updown_counter, observable_counter, observable_updown_counter, histogram, gauge
