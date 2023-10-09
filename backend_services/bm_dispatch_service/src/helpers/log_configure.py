import warnings

from opentelemetry import trace
from opentelemetry.sdk.resources import SERVICE_NAME, SERVICE_NAMESPACE, Resource
from opentelemetry.sdk.trace import TracerProvider

from configs.settings import get_settings
from .otel_helpers import tracing_configuration
from .structlog_helpers import configure_handlers


def configure_logger(app):
    settings = get_settings()
    trace.set_tracer_provider(
        TracerProvider(
            resource=Resource.create({SERVICE_NAME: settings.jaeger_service_name,
                                      SERVICE_NAMESPACE: settings.jaeger_service_namespace
                                      })
        )
    )

    tracing_configuration(
        trace_log_file_path=settings.trace_file_path,
        jaeger_params=settings.jaeger_params,
        app=app,
        # mysql_connection=mysql_connection
    )

    if not settings.debug:
        warnings.filterwarnings("ignore", module="dataclass")
        warnings.filterwarnings("ignore", module="pytest")

    configure_handlers(sterr_log=True, file_log_path=settings.log_file_path, verbose=settings.debug)
