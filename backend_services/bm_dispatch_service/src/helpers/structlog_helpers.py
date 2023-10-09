import logging
from logging.handlers import WatchedFileHandler
from os import makedirs
from pathlib import Path

import structlog
from opentelemetry import baggage, trace
from structlog.contextvars import merge_contextvars


def log_otel_correlator(_, __, dicts):
    active = trace.get_current_span()

    if active:
        context = active.get_span_context()
        if context.trace_id:
            dicts["trace_id"] = f"{context.trace_id:#010x}"

        if context.span_id:
            dicts["span_id"] = f"{context.span_id:#028x}"

        dicts.update(baggage.get_all())

    return dicts


USUAL_STRUCTLOG_PROCESSORS = [
    structlog.processors.add_log_level,
    structlog.stdlib.add_logger_name,
    structlog.processors.TimeStamper(fmt="iso"),
    structlog.processors.format_exc_info,
    structlog.dev.set_exc_info,
    log_otel_correlator,
]

PROCESSORS = USUAL_STRUCTLOG_PROCESSORS + [
    structlog.stdlib.PositionalArgumentsFormatter(),
    structlog.processors.StackInfoRenderer(),
    structlog.processors.format_exc_info,
    merge_contextvars,
    structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
]

structlog.configure(processors=PROCESSORS, logger_factory=structlog.stdlib.LoggerFactory())


def configure_handlers(sterr_log, file_log_path, verbose):
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)

    if sterr_log:
        err_formatter = structlog.stdlib.ProcessorFormatter(
            processors=[structlog.dev.ConsoleRenderer()],
            foreign_pre_chain=USUAL_STRUCTLOG_PROCESSORS,
        )

        err_handler = logging.StreamHandler()
        err_handler.setFormatter(err_formatter)
        err_handler.setLevel(logging.DEBUG if verbose else logging.WARN)

        logger.addHandler(err_handler)

    if file_log_path:
        log_dir = Path(file_log_path).parent
        makedirs(log_dir, exist_ok=True)

        json_formatter = structlog.stdlib.ProcessorFormatter(
            processors=[structlog.processors.JSONRenderer()],
            foreign_pre_chain=USUAL_STRUCTLOG_PROCESSORS,
        )
        json_handler = WatchedFileHandler(file_log_path)
        json_handler.setFormatter(json_formatter)
        logger.addHandler(json_handler)
