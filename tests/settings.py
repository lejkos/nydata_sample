"""Settings module for test app."""
ENV = "development"
TESTING = True
SQLALCHEMY_DATABASE_URI = "sqlite://"
SECRET_KEY = "not-so-secret-in-tests"
JWT_SECRET_KEY = "jwt-not-so-secret-in-tests"
JWT_ACCESS_TOKEN_EXPIRES_IN_SECONDS = 86400

BCRYPT_LOG_ROUNDS = (
    4  # For faster tests; needs at least 4 to avoid "ValueError: Invalid rounds"
)
DEBUG_TB_ENABLED = False
CACHE_TYPE = "simple"  # Can be "memcached", "redis", etc.
SQLALCHEMY_TRACK_MODIFICATIONS = False
WTF_CSRF_ENABLED = False  # Allows form testing
NGINX_ACCESS_LOG_PATH = "tests/test_log/test_access.log"
