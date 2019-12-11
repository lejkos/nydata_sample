# -*- coding: utf-8 -*-
"""The app module, containing the app factory function."""
import logging
import sys

from flask import Flask

from nydata import auth, commands, log_parser, user
from nydata.extensions import (
    bcrypt,
    cache,
    db,
    flask_static_digest,
    jwt,
    login_manager,
    migrate,
)


def create_app(config_object="nydata.settings"):
    """
    Create application factory

    :param config_object: The configuration object to use.
    """
    app = Flask(__name__.split(".")[0])
    app.config.from_object(config_object)
    register_extensions(app)
    register_blueprints(app)
    register_errorhandlers(app)
    register_shellcontext(app)
    register_commands(app)
    configure_logger(app)

    print("[+] App successfully created and configured!")
    return app


def register_extensions(app):
    """Register Flask extensions."""
    bcrypt.init_app(app)
    cache.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    flask_static_digest.init_app(app)

    jwt.init_app(app)
    return None


def register_blueprints(app):
    """Register Flask blueprints."""
    app.register_blueprint(auth.views.blueprint)
    app.register_blueprint(log_parser.views.blueprint)
    return None


def register_errorhandlers(app):
    """Register error handlers."""

    def show_available_urls(error):
        """Show possible entry points"""
        # If a HTTPException, pull the `code` attribute; default to 500

        error_code = getattr(error, "code", 500)
        available_urls = []
        url_methods = dict()

        for rule in app.url_map.iter_rules():
            url = rule.endpoint
            url = "/" + url.replace(".", "/")

            if not url.endswith("/"):
                url += "/"

            if not "static" in url:
                available_urls.append(url)
                url_methods[url] = list(rule.methods)

        return (
            {"available_urls": available_urls, "url_methods": url_methods},
            error_code,
        )

    for errcode in [401, 404, 500]:
        app.errorhandler(errcode)(show_available_urls)
    return None


def register_shellcontext(app):
    """Register shell context objects."""

    def shell_context():
        """Shell context objects."""
        return {"db": db, "User": user.models.User}

    app.shell_context_processor(shell_context)


def register_commands(app):
    """Register CLI Click commands."""
    app.cli.add_command(commands.test)
    app.cli.add_command(commands.add_user)
    app.cli.add_command(commands.read_nginx)
    app.cli.add_command(commands.create_db)


def configure_logger(app):
    """
    Configure loggers.

    We just write to stdout and stderr, see more in the link:
    Point 1 in https://www.loggly.com/blog/best-practices-for-logging-in-docker-swarm/
    """
    handler = logging.StreamHandler(sys.stdout)
    if not app.logger.handlers:
        app.logger.addHandler(handler)
