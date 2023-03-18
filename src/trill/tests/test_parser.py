import pytest
from typing import List

from trill.ast.printer import ASTPrinter

from trill.tests.cases import testcases
from trill.tokenizer import Tokenizer
from trill.parser import Parser
from trill import error_handler


@pytest.mark.parametrize("roll,result", [(case.roll, case.parse_result) for case in testcases if case.parse_result])
def test_parse(roll: str, result: List[str]):
    scanner = Tokenizer(roll)
    tokens = scanner.scan_tokens()
    parser = Parser(tokens)
    expression = parser.parse()
    assert not error_handler.had_error, error_handler.error_report
    res = ASTPrinter().print(expression)
    assert res == result, roll
