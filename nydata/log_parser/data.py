from dataclasses import dataclass
from datetime import datetime

NGINX = "nginx"


@dataclass(frozen=True, eq=True)
class LogEntry:
    """
    General DataClass for a single line of log code.

    The option frozen=True and eq=True make the dataclass
    hashable so we can check for collisions when adding them
    to the database.
    """

    host_ip: str
    original_date_time: datetime
    timestamp: int

    request_verb: str  # GET | POST etc
    request_path: str

    response_code: int
    user_agent: str
