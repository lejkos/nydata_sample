# -*- coding: utf-8 -*-
"""Defines fixtures available to all tests."""

import logging
from dataclasses import dataclass
from os import path

import pytest
from graphene.test import Client
from webtest import TestApp

from nydata.app import create_app
from nydata.database import db as _db
from nydata.log_parser.schema import get_logs_schema

from .factories import UserFactory


@dataclass
class UserData:
    """
    Fake user data for unit tests.
    """

    username: str
    password: str
    email: str
    is_admin: bool


@pytest.fixture
def app():
    """Create application for the tests."""
    _app = create_app("tests.settings")
    _app.logger.setLevel(logging.CRITICAL)
    ctx = _app.test_request_context()
    ctx.push()

    yield _app

    ctx.pop()


@pytest.fixture
def testapp(app):
    """Create Webtest app."""
    return TestApp(app)


@pytest.fixture
def db(app):
    """Create database for the tests."""
    _db.app = app
    with app.app_context():
        _db.create_all()

    yield _db

    # Explicitly close DB connection
    _db.session.close()
    _db.drop_all()


@pytest.fixture
def user_password() -> str:
    return "myprecious"


@pytest.fixture
def user(db, user_password):
    """Create user for the tests."""
    user = UserFactory(password=user_password)
    db.session.commit()
    return user


@pytest.fixture
def test_access_log_path() -> str:
    """
    Get the full path to the access log test file: test_access.log
    """
    return path.abspath("tests/test_log/test_access.log")


@pytest.fixture
def test_bad_log_path() -> str:
    """
    Get the full path to the access log the bad log file: test_access.log
    """
    return path.abspath("tests/test_log/test_bad_file.log")


@pytest.fixture
def access_log_str(test_access_log_path) -> str:
    """The sample access.log as a string"""
    with open(test_access_log_path) as f:
        content = f.read()

    return content


@pytest.fixture
def db_setup_test_nginx_12(test_access_log_path) -> None:
    """
    Populate database with 12 log lines from nginx access.log
    """
    from nydata.log_parser import parse_and_save_nginx_logs

    parse_and_save_nginx_logs(test_access_log_path)


@pytest.fixture
def graphql_client() -> Client:
    """
    Create a GraphQL test client
    """
    schema = get_logs_schema()
    client = Client(schema=schema)
    return client


@pytest.fixture
def log_line() -> str:
    """
    A simple reuseable log line string.
    """
    line = (
        '77.179.66.156 - - [07/Dec/2016:10:34:43 +0100] "GET /favicon.ico HTTP/1.1" '
        '404 571 "http://localhost:8080/" "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_0) '
        'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36"'
    )
    return line


@pytest.fixture
def user_data() -> UserData:
    """
    Some reuseable fake user data
    """
    return UserData(
        username="somebody",
        password="something-really-secret",
        email="tester@nydata.com",
        is_admin=False,
    )
