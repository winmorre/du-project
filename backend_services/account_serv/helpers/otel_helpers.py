import logging
import typing
from logging.handlers import WatchedFileHandler
from os import makedirs
from pathlib import Path

import structlog
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.django import DjangoInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.sdk.trace import ReadableSpan, TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, SpanExportResult, SimpleSpanProcessor, SpanExporter

_Logger = structlog.getLogger(__name__ + ".log")


class AppLogSpanExporter(SpanExporter):
    def __init__(self, logger):
        self.logger = logger

    def export(self, spans: typing.Sequence[ReadableSpan]) -> SpanExportResult:
        for span in spans:
            self.logger.debug(span.to_json(indent=4))

        return SpanExportResult.SUCCESS


def tracing_configuration(trace_log_file_path, jaeger_params=None):
    DjangoInstrumentor().instrument()
    RedisInstrumentor().instrument()

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
    pass


if __name__ == "__main__":
    tracing_configuration("/tmp/account.log")
