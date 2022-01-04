# -*- coding: utf-8 -*-

from logging.config import dictConfig
import pathlib
import os


class Config(object):
    PROJECT_ROOT = pathlib.Path(__file__).parent.parent.absolute()
    SECRET_KEY = os.getenv("SECRET_KEY")
    if "GITHUB_API_KEY" not in os.environ:
        raise KeyError("Missing environment variable {}".format("GITHUB_API_KEY"))
    GITHUB_API_KEY = os.environ.get("GITHUB_API_KEY")


class DevelopmentConfig(Config):
    DEBUG = True
    WTF_CSRF_ENABLED = False


class TestConfig(Config):
    TESTING = True


dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': os.environ.get('LOGLEVEL', 'info').upper(),
        'handlers': ['wsgi']
    },
    'loggers': {
        'urllib3.connectionpool': {
            'level': os.environ.get('CONNECTIONPOOL_LOGLEVEL', 'info').upper(),
            'handlers': ['wsgi']
        }
    }
})
