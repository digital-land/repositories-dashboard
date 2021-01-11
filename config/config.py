# -*- coding: utf-8 -*-

import pathlib
import os


class Config(object):
    PROJECT_ROOT = pathlib.Path(__file__).parent.parent.absolute()
    SECRET_KEY = os.getenv("SECRET_KEY")
    GITHUB_API_KEY = os.getenv("GITHUB_API_KEY", False)


class DevelopmentConfig(Config):
    DEBUG = True
    WTF_CSRF_ENABLED = False


class TestConfig(Config):
    TESTING = True
