# -*- coding: utf-8 -*-

import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType
from graphql import GraphQLError

from nydata.log_parser.models import LogLine


class Log(SQLAlchemyObjectType):
    """
    GraphQL Object type definition of a db.LogLine object
    """

    class Meta:
        model = LogLine
        interfaces = (graphene.relay.Node,)


class Query(graphene.ObjectType):
    """
    NyData allowed log query definition.
    """

    logs = graphene.List(
        Log,
        date_from=graphene.Date(required=True),
        date_to=graphene.Date(required=True),
    )

    def resolve_logs(self, info, date_from, date_to):

        if date_from > date_to:
            msg = (
                "[!] Invalid query `date_from` always has to be smaller than `date_to`!"
            )
            raise GraphQLError(msg)

        #  date_from <= LogLine.date <= date_to
        lines = LogLine.query.filter(
            LogLine.date >= date_from, LogLine.date <= date_to
        ).all()
        return lines


def get_logs_schema() -> graphene.Schema:
    """
    Get a graphene Schema instace for a nydata.logs schema.
    """
    logs_schema = graphene.Schema(query=Query, auto_camelcase=False)
    return logs_schema


schema = graphene.Schema(query=Query)
