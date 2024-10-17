import logging

from azure.monitor.opentelemetry import configure_azure_monitor
from shared.config import settings
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource


def enable_logging() -> None:
    """Initializes the logging via open telemetry for the bot framework.

    RETURNS (None): No return value.
    """
    # Configure base logger
    log_level = logging.DEBUG if settings.DEBUG else settings.LOGGING_LEVEL
    logging.basicConfig(format="%(asctime)s:%(levelname)s:%(message)s", level=log_level)

    # Configure azure monitor logs
    configure_azure_monitor(
        connection_string=settings.APPLICATIONINSIGHTS_CONNECTION_STRING,
        # Use below configuration to turn instrumentations on/off
        # instrumentation_options={
        #     "azure_sdk": {"enabled": True},
        #     "django": {"enabled": False},
        #     "fastapi": {"enabled": False},
        #     "flask": {"enabled": True},
        #     "psycopg2": {"enabled": False},
        #     "requests": {"enabled": False},
        #     "urllib": {"enabled": False},
        #     "urllib3": {"enabled": False},
        # },
        resource=Resource.create(
            {
                "service.name": settings.SERVER_NAME,
                "service.namespace": settings.PROJECT_NAME,
                "service.instance.id": settings.WEBSITE_INSTANCE_ID,
            }
        ),
        logger_name=settings.PROJECT_NAME,
        enable_live_metrics=True,
    )


def get_logger(name: str) -> logging.Logger:
    """Creates and returns a logger instance with the configured logging level that is connected to the open telemetry exporter.

    name (str): Child name of the logger.
    RETURNS (Logger): Returns a logger instance to capture logs.
    """
    # Init logger
    logger = logging.getLogger(f"{settings.PROJECT_NAME}.{name}")

    # Set log level
    log_level = logging.DEBUG if settings.DEBUG else settings.LOGGING_LEVEL
    logger.setLevel(log_level)

    return logger


def get_tracer(name: str) -> trace.Tracer:
    """Creates and returns a tracer instance with the configured logging level that is connected to the open telemetry exporter.

    name (str): Child name of the tracer.
    RETURNS (Tracer): Returns a tracer instance to capture traces.
    """
    # Init tracer
    tracer = trace.get_tracer(f"{settings.PROJECT_NAME}.{name}")

    return tracer
