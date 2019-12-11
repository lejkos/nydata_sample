from functools import partial
from typing import Dict, List

from nydata.error import LogRegexPatternNotFound, LogTransformerNotFound
from nydata.log_parser.data import NGINX, LogEntry
from nydata.utils import extract_and_transform

from .pattern import get_patterns
from .transform import get_transformers


def generic_parse_logs(
    regexes: Dict, transformers: Dict, source_type: str, log_file: str
) -> List[LogEntry]:
    """
    Parse a log string into a list of LogEntries.
    """
    pattern = regexes.get(source_type)
    transform = transformers.get(source_type)

    if pattern is None:
        msg = f"No pattern found with the name=`{source_type}`!"
        raise LogRegexPatternNotFound(msg)

    if transform is None:
        msg = f"No transformer found with the name=`{source_type}`!"
        raise LogTransformerNotFound(msg)

    # preparing the line parser
    parse_line = partial(extract_and_transform, pattern, transform)

    return [parse_line(line) for line in log_file.splitlines()]


def generic_parse_log_line(
    regexes: Dict, transformers: Dict, source: str, line: str
) -> LogEntry:
    """
    A generic parser function to parse and transfer a log line string
    to a LogLine entry
    """
    pattern = regexes.get(source)
    transform = transformers.get(source)

    if pattern is None:
        msg = f"No pattern found with the name=`{source}`!"
        raise LogRegexPatternNotFound(msg)

    if transform is None:
        msg = f"No transformer found with the name=`{source}`!"
        raise LogTransformerNotFound(msg)

    return extract_and_transform(pattern, transform, line)


parse_log_line = partial(generic_parse_log_line, get_patterns(), get_transformers())
parse_nginx_log_line = partial(parse_log_line, NGINX)

parse_logs = partial(generic_parse_logs, get_patterns(), get_transformers())
parse_nginx_logs = partial(parse_logs, NGINX)
