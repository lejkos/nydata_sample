# -*- coding: utf-8 -*-

from typing import Dict

from dateutil import parser

from nydata.log_parser.data import NGINX, LogEntry


def transform_nginx(log_entry: Dict) -> LogEntry:
    """
    Transform a nginx dict to a LogEntry
    """

    # a small closure for better readability
    def get(name: str, default=""):
        return log_entry.get(name, default)

    original_date_time = parser.parse(get("time"), fuzzy=True)
    timestamp = int(original_date_time.timestamp())
    code = int(get("code"))

    return LogEntry(
        host_ip=get("ip"),
        original_date_time=original_date_time,
        timestamp=timestamp,
        request_verb=get("verb"),
        request_path=get("path"),
        response_code=code,
        user_agent=get("agent"),
    )


_TRANSFORMERS = {
    NGINX: transform_nginx,
}


def get_transformers() -> Dict:
    """
    Access the transformer mapper
    """
    return _TRANSFORMERS
