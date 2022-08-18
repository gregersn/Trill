import pytest
from trill.tokenizer import Scanner
from trill.error import handler as error_handler


@pytest.mark.parametrize("source, is_error", [("36d%4", True), ("4$", True), ("4d6", False)])
def test_scanner_errors(source: str, is_error: bool):
    scanner = Scanner(source)
    scanner.scan_tokens()
    assert error_handler.had_error == is_error
