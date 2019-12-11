import pytest

from nydata.log_parser import digest_log_by_line, digest_logs, parse_and_save_nginx_logs
from nydata.log_parser.data import NGINX
from nydata.log_parser.models import LogLine, LogSource


@pytest.mark.usefixtures("db")
def test_parse_and_save_nginx_log(test_access_log_path):

    assert LogLine.query.count() == 0
    assert LogSource.query.count() == 0

    saved = parse_and_save_nginx_logs(test_access_log_path)
    assert saved is True

    assert LogSource.query.count() == 1
    assert LogLine.query.count() == 12


@pytest.mark.usefixtures("db")
def test_parse_and_save_nginx_log__bad_log_file(test_bad_log_path):

    assert LogLine.query.count() == 0
    assert LogSource.query.count() == 0

    saved = parse_and_save_nginx_logs(test_bad_log_path)
    assert saved is False

    # we add a new log source bad no log lines.
    assert LogSource.query.count() == 1
    assert LogLine.query.count() == 0


@pytest.mark.usefixtures("db")
def test_parse_and_save_nginx_log__file_does_not_exist():

    assert LogLine.query.count() == 0
    assert LogSource.query.count() == 0

    saved = parse_and_save_nginx_logs("file/does/not/exist")
    assert saved is False


@pytest.mark.usefixtures("db")
def test_parse_and_save_nginx_log__save_by_line(test_access_log_path):

    assert LogLine.query.count() == 0
    assert LogSource.query.count() == 0

    saved = parse_and_save_nginx_logs(test_access_log_path, 0.00001)
    assert saved is True

    assert LogSource.query.count() == 1
    assert LogLine.query.count() == 12


@pytest.mark.usefixtures("db")
def test_digest_log_by_line(test_access_log_path):

    assert LogLine.query.count() == 0
    assert LogSource.query.count() == 0

    saved = digest_log_by_line(NGINX, test_access_log_path)
    assert saved is True

    assert LogSource.query.count() == 1
    assert LogLine.query.count() == 12


@pytest.mark.usefixtures("db")
def test_digest_logs(test_access_log_path):

    assert LogLine.query.count() == 0
    assert LogSource.query.count() == 0

    saved = digest_logs(NGINX, test_access_log_path)
    assert saved is True

    assert LogSource.query.count() == 1
    assert LogLine.query.count() == 12


@pytest.mark.usefixtures("db")
def test_digest_logs(test_bad_log_path):
    """
    """
    assert LogLine.query.count() == 0
    assert LogSource.query.count() == 0

    saved = digest_log_by_line(NGINX, test_bad_log_path)
    assert saved is False

    assert LogSource.query.count() == 1
    assert LogLine.query.count() == 0
