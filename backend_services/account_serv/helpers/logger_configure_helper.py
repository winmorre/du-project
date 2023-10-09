import warnings

from django.conf import settings
from opentelemetry import trace
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider

from helpers.otel_helpers import tracing_configuration
from helpers.structlog_helpers import configure_handlers


def configure_logger():
    trace.set_tracer_provider(
        TracerProvider(resource=Resource.create({SERVICE_NAME: settings.JAEGER_PARAMS.get("service_name")}))
    )

    tracing_configuration(trace_log_file_path=settings.ACCOUNT_SERVICE_TRACE_PATH, jaeger_params=settings.JAEGER_PARAMS)

    if not settings.DEBUG:
        warnings.filterwarnings("ignore", module="dataclass")

    configure_handlers(sterr_log=True, file_log_path=settings.ACCOUNT_SERVICE_LOG_PATH, verbose=settings.DEBUG)
