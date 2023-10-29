from logging import config as cfg


def init_logger(env: str):
    default_logging = {
        # this is required
        "version": 1,
        # Disable other logger, Default True
        "disable_existing_loggers": False,
        # filter setting
        "filters": {},
        # formatter setting
        "formatters": {
            "basic": {
                "format": "%(asctime)s %(levelname)s: %(message)s",
            },
        },
        # handler setting
        "handlers": {
            "console": {
                "level": "DEBUG",
                "class": "logging.StreamHandler",
                "formatter": "basic",
            },
        },
        # make logger
        "loggers": {},
        # root logger setting
        "root": {
            "handlers": ["console"],
            # depends on env
            "level": "DEBUG" if env.lower() != "production" else "INFO",
        },
    }
    # config set
    cfg.dictConfig(default_logging)
