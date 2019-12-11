# -*- coding: utf-8 -*-
from flask import Blueprint
from flask_graphql import GraphQLView
from flask_jwt_extended import jwt_required

from ..settings import NGINX_ACCESS_LOG_PATH
from .log import parse_and_save_nginx_logs
from .schema import schema


def graphql_view():
    """
    Create a GraphQL interface with GraphiQL
    and protected through an access token.
    """
    view = GraphQLView.as_view("", schema=schema, graphiql=False)
    return jwt_required(view)


# Opt-out of CSRF protection for GraphQL interface.
blueprint = Blueprint(
    "graphql", __name__, url_prefix="/graphql", static_folder="../static"
)

# view_func = GraphQLView.as_view('', schema=schema, graphiql=True)
blueprint.add_url_rule("/", view_func=graphql_view())


@blueprint.before_app_first_request
def read_access_log():
    """
    Read access log before first request.

    In a productive solution I would query it regularly with
    Celery beat in another process.
    """
    log_path = NGINX_ACCESS_LOG_PATH
    parse_and_save_nginx_logs(log_path)
