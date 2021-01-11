# -*- coding: utf-8 -*-
import os
from flask import Flask, render_template
from flask.cli import load_dotenv
from jinja2 import PackageLoader, PrefixLoader, ChoiceLoader

if os.environ["FLASK_ENV"] == "production":
    dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
    load_dotenv(dotenv_path)


def create_app(config_filename):
    app = Flask(__name__)
    app.config.from_object(config_filename)
    register_errorhandlers(app)
    register_blueprints(app)
    register_filters(app)
    #register_templates(app)
    return app


def register_errorhandlers(app):
    def render_error(error):
        # If a HTTPException, pull the `code` attribute; default to 500
        error_code = getattr(error, "code", 500)
        return render_template("error/{0}.html".format(error_code)), error_code

    for errcode in [400, 401, 404, 500]:
        app.errorhandler(errcode)(render_error)
    return None


def register_blueprints(app):
    from application.blueprints.frontend.views import frontend
    app.register_blueprint(frontend)


def register_filters(app):
    from application.utils.filters import format_date
    app.add_template_filter(format_date)


# def register_templates(app):
#     # register govuk components
#     govuk_components.init_app(app)
#     # register digital land components
#     multi_loader = ChoiceLoader([
#         app.jinja_loader,
#         PrefixLoader(
#             {
#                 "digital-land-frontend": PackageLoader(
#                     "digital_land_frontend"
#                 ),
#             }
#         )
#     ])
#     app.jinja_loader = multi_loader
