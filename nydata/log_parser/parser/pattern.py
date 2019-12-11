import re
from typing import Dict

from nydata.log_parser.data import NGINX

_NGINX_LOG_LINE = r"""^(?P<ip>[0-9.]*)    # ip entry
                     \s*-\s*-\s*
                     \[(?P<time>.*?)\]   # datetime entry
                     \s"
                     (?P<verb>[A-Z]*)    # HTTP method like GET, HEAD
                     \s
                     (?P<path>.*?)
                     \sHTTP/\d\.\d"\s
                     (?P<code>\d{3})     # HTTP status code
                     \s\d*\s".*?"\s
                     "(?P<agent>.*?)"    # agent
                     $"""


def get_nginx_log_regex() -> re.Pattern:
    """
    Retrieve a compiled regexp
    """
    return re.compile(_NGINX_LOG_LINE, re.VERBOSE)


_PATTERNS = {
    NGINX: get_nginx_log_regex(),
}


def get_patterns() -> Dict:
    """
    Get the name <-> pattern mapper.
    """
    return _PATTERNS
