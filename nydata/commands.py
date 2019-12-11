# -*- coding: utf-8 -*-
"""Click commands."""
import os
import sys
from os import path

import click
from flask.cli import with_appcontext

from .log_parser import parse_and_save_nginx_logs
from .user.models import add_user as add_user_to_model
from .utils import eprint
from .settings import SQLALCHEMY_DATABASE_URI

HERE = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.join(HERE, os.pardir)
TEST_PATH = os.path.join(PROJECT_ROOT, "tests")


@click.command("adduser", help="Create an api user")
@click.argument("username", required=True, type=str)
@click.argument("password", required=True, type=str)
@click.argument("email", required=True, type=str)
@click.option("--is-admin", required=False, default=False, is_flag=True, type=bool)
@with_appcontext
def add_user(username, password, email, is_admin):
    """
    Add an API user to the application
    """
    try:
        user = add_user_to_model(
            username=username, password=password, email=email, is_admin=is_admin
        )
        print(f"[+] SUCCESS: Created user={user.username}!")

    except Exception as error:
        eprint(f"[-] Failed to create username={username}!")
        eprint(error)
        sys.exit(1)


@click.command("read-nginx")
@click.argument("location", required=True, type=str)
@with_appcontext
def read_nginx(location):
    """
    Read a certain nginx access.log file
    """

    if not path.exists(location):
        eprint(f"[-] Location does not exist {location}!")
        eprint(f"[-] Exiting!")
        sys.exit(1)

    try:
        parse_and_save_nginx_logs(location)
    except Exception as error:
        eprint(f"[-] Could not parse logs from location=`{location}`")
        eprint(f"[-] Error {error}")
        sys.exit(1)


@click.command("test")
def test():
    """Run the tests."""
    from os import system
    system("pytest")


@click.command("createdb")
def create_db():

    from sqlalchemy_utils import database_exists, create_database
    print(f'[+] Does the db exist={SQLALCHEMY_DATABASE_URI}?')

    if not database_exists(SQLALCHEMY_DATABASE_URI):
        print('[+] Trying to create database')
        create_database(SQLALCHEMY_DATABASE_URI)