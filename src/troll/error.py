"""Error handling."""
from typing import List

had_error: bool = False
error_report: List[str] = []


def error(line: int, message: str):
    report(line, "", message)


def report(line: int, _: str, message: str):
    global had_error  # pylint: disable=global-statement
    error_report.append(f"[line {line}] Error: {message}")
    had_error = True


def reset():
    global had_error  # pylint: disable=global-statement
    had_error = False
    error_report.clear()
