"""Error handling."""
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Error:
    line: int
    column: int
    message: Optional[str] = None


@dataclass
class ScannerError(Error):
    ...


@dataclass
class ParserError(Error):

    def __str__(self):
        if self.message is None:
            return f"Parser-error at line {self.line}, column {self.column}"
        return f"Parser-error at line {self.line}, column {self.column}: {self.message}"


@dataclass
class InterpreterError(Error):
    ...


class ErrorHandler:
    had_error: bool = False
    error_report: List[Error] = []

    def __init__(self):
        ...

    def reset(self):
        self.had_error = False
        self.error_report.clear()

    def report(self, error: Error):
        self.had_error = True
        self.error_report.append(error)


handler = ErrorHandler()
