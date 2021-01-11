# -*- coding: utf-8 -*-

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
