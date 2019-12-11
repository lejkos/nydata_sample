import pytest

from nydata.error import LogRegexPatternNotFound, LogTransformerNotFound
from nydata.log_parser import NGINX
from nydata.log_parser.parser import (
    parse_log_line,
    parse_logs,
    parse_nginx_log_line,
    parse_nginx_logs,
)
from nydata.log_parser.parser.parser import generic_parse_log_line, generic_parse_logs


def test_parse_logs():
    """
    Test the generic log parser
    """
    with open("tests/test_log/test_access.log") as fconn:
        log_entries = parse_logs(NGINX, fconn.read())
        log_entry = log_entries[0]

        assert len(log_entries) == 12

        assert log_entry.host_ip == "77.179.66.156"
        assert log_entry.request_verb == "GET"
        assert log_entry.request_path == "/"

        agent = (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_0) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/54.0.2840.59 Safari/537.36"
        )

        assert log_entry.user_agent == agent


def test_parse_nginx_logs():
    """
    Test the specific nginx log parser
    """
    with open("tests/test_log/test_access.log") as fconn:
        log_entries = parse_nginx_logs(fconn.read())
        log_entry = log_entries[0]

        assert len(log_entries) == 12

        assert log_entry.host_ip == "77.179.66.156"
        assert log_entry.request_verb == "GET"
        assert log_entry.request_path == "/"

        agent = (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_0) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/54.0.2840.59 Safari/537.36"
        )

        assert log_entry.user_agent == agent


def test_parse_log_line(log_line):
    """
    Test generic log line parser
    """
    log_entry = parse_log_line(NGINX, log_line)
    assert log_entry.host_ip == "77.179.66.156"


def test_parse_nginx_log_line(log_line):
    """
    Test specific nginx log line parser
    """
    log_entry = parse_nginx_log_line(log_line)
    assert log_entry.host_ip == "77.179.66.156"


def test_generic_parse_log_line_regexp_not_found():
    with pytest.raises(LogRegexPatternNotFound):
        generic_parse_log_line(
            regexes={}, transformers={"nginx": None}, source="nginx", line="log line"
        )


def test_generic_parse_log_line__transformer_not_found():
    with pytest.raises(LogTransformerNotFound):
        generic_parse_log_line(
            regexes={"nginx": "some pattern"},
            transformers={},
            source="nginx",
            line="log line",
        )


def test_generic_parse_logs_regexp_not_found():
    with pytest.raises(LogRegexPatternNotFound):
        generic_parse_logs(
            regexes={},
            transformers={"nginx": None},
            source_type="nginx",
            log_file="log file str",
        )


def test_generic_parse_logs__transformer_not_found():
    with pytest.raises(LogTransformerNotFound):
        generic_parse_logs(
            regexes={"nginx": "some pattern"},
            transformers={},
            source_type="nginx",
            log_file="log line",
        )
