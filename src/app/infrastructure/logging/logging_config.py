from logging.config import dictConfig

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "add_correlation_id": {
            "()": "app.infrastructure.logging.logger_with_correlation_id.CorrelationIdFilter"
        }
    },
    "formatters": {
        "default": {
            "format": "%(asctime)s [%(levelname)s] %(name)s "
            "[correlation_id=%(correlation_id)s] %(message)s"
        }
    },
    "handlers": {
        "default": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "filters": ["add_correlation_id"],
        }
    },
    "root": {"level": "INFO", "handlers": ["default"]},
}


def setup_logging() -> None:
    dictConfig(LOGGING)
