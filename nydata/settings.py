# -*- coding: utf-8 -*-
"""Application configuration.

Most configuration is set via environment variables.

For local development, use a .env file to set
environment variables.
"""
from os import path

from environs import Env

env = Env()
env.read_env()

ENV = env.str("FLASK_ENV", default="production")
DEBUG = ENV == "development"
SQLALCHEMY_DATABASE_URI = env.str("DATABASE_URL")
SECRET_KEY = env.str("SECRET_KEY")
JWT_SECRET_KEY = env.str("JWT_SECRET_KEY")
JWT_ACCESS_TOKEN_EXPIRES = int(env.str("JWT_ACCESS_TOKEN_EXPIRES_IN_SECONDS"))

SEND_FILE_MAX_AGE_DEFAULT = env.int("SEND_FILE_MAX_AGE_DEFAULT")
BCRYPT_LOG_ROUNDS = env.int("BCRYPT_LOG_ROUNDS", default=13)
DEBUG_TB_ENABLED = DEBUG
DEBUG_TB_INTERCEPT_REDIRECTS = False
CACHE_TYPE = "simple"  # Can be "memcached", "redis", etc.
SQLALCHEMY_TRACK_MODIFICATIONS = False

POSTGRES_URL = env.str('POSTGRES_URL')
POSTGRES_PORT = env.str('POSTGRES_PORT')
POSTGRES_USER = env.str('POSTGRES_USER')
POSTGRES_PASSWORD = env.str('POSTGRES_PASSWORD')
POSTGRES_DB = env.str('POSTGRES_DB')


SQLALCHEMY_DATABASE_URI = f'postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}' \
                          f'@{POSTGRES_URL}:{POSTGRES_PORT}/{POSTGRES_DB}'

SQLALCHEMY_TRACK_MODIFICATIONS = False

NGINX_ACCESS_LOG_PATH = path.abspath(env.str("NGINX_ACCESS_LOG_PATH"))
msg = f"[-] Bad configuration! Log file does not exist: path=`{NGINX_ACCESS_LOG_PATH}`"
assert path.exists(NGINX_ACCESS_LOG_PATH), msg
