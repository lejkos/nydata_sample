from copy import deepcopy
from datetime import datetime

import pytest

from nydata.database import get_or_create
from nydata.error import LogLineAlreadyInDb
from nydata.log_parser.data import NGINX, LogEntry
from nydata.log_parser.models import (
    LogLine,
    LogSource,
    create_log_line,
    save_logs_to_database,
)
from nydata.log_parser.parser.parser import parse_logs, parse_nginx_logs


@pytest.mark.usefixtures("db")
def test_initialize_log_source():
    source = LogSource.create(name="nginx")
    assert source.name == "nginx"


@pytest.mark.usefixtures("db")
def test_create_a_logline():

    source = LogSource.create(name="nginx")
    assert source.name == "nginx"

    now = datetime.now()
    timestamp = int(now.timestamp())
    ip = "127.0.0.1"

    verb = "GET"
    request_path = "/robots.txt"
    response_code = 200

    user_agent = "Mozilla..."

    line = LogLine.create(
        log_source_id=source.id,
        hostIP=ip,
        date=now.date(),
        timestamp=timestamp,
        verb=verb,
        path=request_path,
        code=response_code,
        userAgent=user_agent,
    )

    assert line.userAgent == user_agent

    # let's check if the relationships are fine
    assert line.log_source.name == "nginx"

    # check the rest
    assert line.hostIP == ip
    assert line.verb == verb
    assert line.path == request_path

    assert line.timestamp == timestamp
    assert line.date == now.date()


@pytest.mark.usefixtures("db")
def test_save_logs_to_database(access_log_str):

    lines = parse_nginx_logs(access_log_str)
    save_logs_to_database("nginx", lines)

    assert LogLine.query.count() == 12


@pytest.mark.usefixtures("db")
def test_save_logs_to_database_with_parse_logs(access_log_str):

    lines = parse_logs(NGINX, access_log_str)
    save_logs_to_database("nginx", lines)

    assert LogLine.query.count() == 12


@pytest.mark.usefixtures("db")
def test_save_logs_to_database_with_parse_logs__error_with_empty_source(access_log_str):

    lines = parse_logs(NGINX, access_log_str)
    saved = save_logs_to_database("", lines)
    assert saved is False


def create_entry(verb, now) -> LogEntry:
    """Create a log entry"""
    return LogEntry(
        host_ip="127.0.0.1",
        original_date_time=now,
        timestamp=int(now.timestamp()),
        request_verb=verb,
        request_path="/favicon.ico",
        response_code=200,
        user_agent="Mozilla",
    )


def test_log_entry_is_hashable():

    now = datetime.now()
    entry = create_entry("GET", now)
    assert hash(entry) == hash(entry)


def test_log_entry_is_hashable__with_different_datetime_objects():

    now1 = datetime.now()
    now2 = deepcopy(now1)
    entry1 = create_entry("GET", now1)
    entry2 = create_entry("GET", now2)
    assert hash(entry1) == hash(entry2)


def test_log_entries_create_different_hashes():
    now = datetime.now()

    entry1 = create_entry("GET", now)
    entry2 = create_entry("POST", now)
    assert hash(entry1) != hash(entry2)


@pytest.mark.usefixtures("db")
def test_create_log_line(db):

    assert LogLine.query.count() == 0
    source_obj = get_or_create(db.session, LogSource, name=NGINX)

    now = datetime.now()
    entry1 = create_entry("GET", now)

    create_log_line(source_obj.id, entry1)

    assert LogLine.query.count() == 1


@pytest.mark.usefixtures("db")
def test_create_log_line__already_in_db_error(db):

    assert LogLine.query.count() == 0
    source_obj = get_or_create(db.session, LogSource, name=NGINX)

    now = datetime.now()
    entry1 = create_entry("GET", now)

    create_log_line(source_obj.id, entry1)
    assert LogLine.query.count() == 1

    with pytest.raises(LogLineAlreadyInDb):
        create_log_line(source_obj.id, entry1)

    assert LogLine.query.count() == 1


@pytest.mark.usefixtures("db")
def test_create_log_line__already_in_db_error_other_object(db):

    assert LogLine.query.count() == 0
    source_obj = get_or_create(db.session, LogSource, name=NGINX)

    now = datetime.now()
    entry1 = create_entry("GET", now)

    create_log_line(source_obj.id, entry1)
    assert LogLine.query.count() == 1

    # same data but different object
    entry2 = create_entry("GET", now)

    with pytest.raises(LogLineAlreadyInDb):
        create_log_line(source_obj.id, entry2)

    assert LogLine.query.count() == 1
