# -*- coding: utf-8 -*-

import pathlib
import os


class Config(object):
    PROJECT_ROOT = pathlib.Path(__file__).parent.parent.absolute()
    SECRET_KEY = os.getenv("SECRET_KEY")
    if "GITHUB_API_KEY" not in os.environ:
        raise KeyError("Missing environment variable {}".format("GITHUB_API_KEY"))
    GITHUB_API_KEY = os.environ.get("GITHUB_API_KEY")
    AWS_DEFAULT_REGION = os.environ.get('AWS_DEFAULT_REGION')
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    AWS_SESSION_TOKEN = os.environ.get('AWS_SESSION_TOKEN')  # Only needed for temporary credentials


class DevelopmentConfig(Config):
    DEBUG = True
    WTF_CSRF_ENABLED = False


class TestConfig(Config):
    TESTING = True
