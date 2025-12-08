import logging
from logging.config import dictConfig
from .logging_context import UserContextFilter
import os

# logging configuration in the form of a dictionary

def logging_setup():
    os.makedirs("logs",exist_ok=True)

    
    logging_config = {
        "version":1,
        "disable_existing_loggers":False,
        "formatters":{
            "default":{
                "format":"[%(asctime)s] [user=%(user_id)s] %(levelname)s in %(module)s: %(message)s"
            },
            "detailed":{
                "format":"[%(asctime)s] [user=%(user_id)s] %(levelname)s [%(name)s:%(lineno)d] %(message)s"
            },

        },

        "filters":{
            "user_context":{
                "()":UserContextFilter,
            },
        },

        "handlers":{
            "console":{
                "class":"logging.StreamHandler",
                "formatter":"default",
                "filters":["user_context"]
            },
            "file":{
                "class":"logging.handlers.RotatingFileHandler",
                "formatter":"detailed",
                "filters":["user_context"],
                "filename":"logs/app.log",
                "encoding":"utf-8",
                "maxBytes":1048576,
                "backupCount":7,
            },
        },
        "root":{
            "level":"INFO",
            "handlers":["console", "file"],
        },
            }
    
    dictConfig(logging_config)
    return logging.getLogger("fintech")