from os import path

from ..utils import eprint
from .data import NGINX
from .models import save_log_to_database, save_logs_to_database
from .parser.parser import parse_log_line, parse_logs

BIG_FILE_SIZE_IN_MB = 100


def parse_and_save_nginx_logs(
    file_path: str, parse_by_line_at_mb: float = BIG_FILE_SIZE_IN_MB
) -> bool:
    """
    Parse and save NGINX access log files from a certain location

    The parameter parse_by_line_at_mb chooses the parsing mode.
    If the log file is bigger than this size it will be parsed
    line by line.
    """
    try:
        size_in_mb = path.getsize(file_path) / 1_000_000.0
        bigger_than_threshold = size_in_mb > parse_by_line_at_mb

        if bigger_than_threshold:
            return digest_log_by_line(NGINX, file_path)

        else:
            return digest_logs(NGINX, file_path)

    except Exception as error:
        eprint(f"[-] Failed to parse and save access.log at location={file_path}")
        eprint(f"[-] Retrieved error: {error}")
        return False


def digest_log_by_line(source: str, file_path: str) -> bool:
    """
    Parse and save nginx log files to the database.
    The parameter source specifies

    Attention: This function works line by line and
    in order to save memory
    """
    num_errors = 0
    failed_lines = []
    # only reads one line - when the next line is loaded
    # the previous one is garbage collected.
    with open(file_path) as file_conn:
        for line in file_conn:
            try:
                log_entry = parse_log_line(source, line)
                save_log_to_database(source, log_entry)

            except Exception as error:
                eprint(f"[-] Failed to save log to db: {error}")
                eprint(f"[-] Failed line: {line}")
                num_errors += 1
                failed_lines.append(line)
                continue

    if num_errors == 0:
        return True
    else:
        eprint(f"[-] Failed log lines: {failed_lines}")
        eprint(f"[-] Number of failed lines: {num_errors}!")
        return False


def digest_logs(source: str, file_path: str) -> bool:
    """
    :param: source which type of log file are we dealing with.
    :param: file_path: The full fill path to the log
    """
    print(f"[+] Trying parse nginx access.log from path={file_path}")

    with open(file_path) as f:
        log_file_content = f.read()

    log_entries = parse_logs(source, log_file_content)
    num_entries = len(log_entries)

    print(f"[+] Parsing OK. Number of found entries={num_entries}")
    saved = save_logs_to_database(NGINX, log_entries)
    return saved
