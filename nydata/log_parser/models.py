from typing import List

from nydata.database import Column, Model, SurrogatePK, db, get_or_create, relationship

from ..error import LogLineAlreadyInDb
from ..utils import eprint
from .data import LogEntry


class LogSource(SurrogatePK, Model):
    """
    Where the log was taken from e.g. nginx
    """

    __tablename__ = "log_sources"

    name = Column(db.String(80), unique=True)
    lines = relationship("LogLine", backref="log_source")


class LogLine(SurrogatePK, Model):
    """The parsed and normalized log line"""

    __tablename__ = "log_lines"

    # log_source = relationship('LogSource', backref='log_sources')
    log_source_id = Column(db.Integer(), db.ForeignKey("log_sources.id"))

    # can contain IPv4 and IPv6
    hostIP = Column(db.String(40))

    date = Column(db.Date(), index=True)
    timestamp = Column(db.Integer())

    # RFC 7231 section 4 and RFC 5789 section 2
    verb = Column(db.String(8))

    # https://stackoverflow.com/questions/417142/what-is-the-maximum-length-of-a-url-in-different-browsers
    path = Column(db.String(2043))
    code = Column(db.Integer())
    userAgent = Column(db.Text())

    # Hash code for collision checks
    hash_code = Column(db.String(128), index=True)


def create_log_line(log_source_id: int, entry: LogEntry, commit=True) -> LogLine:
    """
    Create a models.LogLine from a LogEntry dataclass.
    """
    date = entry.original_date_time.date()
    hash_code = str(hash(entry))

    # https://stackoverflow.com/questions/32938475/flask-sqlalchemy-check-if-row-exists-in-table
    log_line_not_in_db = LogLine.query.filter_by(hash_code=hash_code).scalar() is None

    if log_line_not_in_db:
        return LogLine.create(
            commit=commit,
            log_source_id=log_source_id,
            hostIP=entry.host_ip,
            date=date,
            timestamp=entry.timestamp,
            verb=entry.request_verb,
            path=entry.request_path,
            code=entry.response_code,
            userAgent=entry.user_agent,
            hash_code=hash_code,
        )
    else:
        msg = "[-] LogLine already in database. Skipping"
        raise LogLineAlreadyInDb(msg)


def save_log_to_database(source: str, log_entry: LogEntry) -> bool:
    """
    Save a single log entry to the database.
    """
    try:
        print(f"[+] Inserting log to db for source={source}")
        log_source = get_or_create(db.session, LogSource, name=source)
        create_log_line(log_source.id, log_entry)

    except LogLineAlreadyInDb:
        eprint(f"[-] LogLine already in DB - skip!")
        return False

    except Exception as error:
        eprint(f"[-] Could not write LogEntry to db: {log_entry}")
        raise error


def save_logs_to_database(source: str, logs: List[LogEntry]) -> bool:
    """
    Save a list of log entries to the database.
    """
    try:
        print(f"[+] Inserting parsed logs to db for source={source}")
        assert source, "[-] The name of LogSource cannot be empty!"
        log_source = get_or_create(db.session, LogSource, name=source)

        db_log_lines = []

        for log_line in logs:
            if log_line is None:
                continue
            try:
                db_obj = create_log_line(log_source.id, log_line, commit=False)
                db_log_lines.append(db_obj)

            # Skip added lines
            except LogLineAlreadyInDb:
                continue

        # db_log_lines = [create_log_line(log_source.id, log_line, commit=False)
        #                 for log_line in logs
        #                 if log_line is not None]

        if len(db_log_lines) == 0:
            eprint(f"[-] 0 log lines retrieved!")
            return False

        # db.session.add_all(db_log_lines)
        # Flush the whole data to db.
        db.session.commit()

        num_lines = len(db_log_lines)
        print(f"[+] SUCCESS. Added {num_lines} log lines to db!")
        return True

    except Exception as error:
        eprint("[-] Could not save logs to db -> Rollback!")
        eprint(f"[-] Error: {error}")

        db.session.rollback()

        eprint(f"[-] Rollback successful!")
        return False
