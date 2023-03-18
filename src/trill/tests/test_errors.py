import pytest
from trill.tokenizer import Tokenizer
from trill.error import handler as error_handler
from trill import trill
from trill.tests.cases import testcases


@pytest.mark.parametrize("source, is_error", [("36d%4", True), ("4$", True), ("4d6", False)])
def test_scanner_errors(source: str, is_error: bool):
    scanner = Tokenizer(source)
    scanner.scan_tokens()
    assert error_handler.had_error == is_error


@pytest.mark.parametrize("roll,error", [(case.roll, case.error) for case in testcases if case.error])
def test_error(roll: str, error: str):
    res, err = trill(roll)
    assert res is None
    assert err is not None
    assert str(err[0]) == error
