"""Test miscellanous Troll rolls."""
from typing import Any, List

import pytest

from trill.interpreter import Interpreter
from trill.parser import Parser
from trill.tokenizer import Scanner
from trill.ast.printer import ASTPrinter

from .cases import testcases


@pytest.mark.parametrize("roll,result", [(case.roll, case.token_count) for case in testcases if case.token_count])
def test_tokenizer(roll: str, result: int):
    scanner = Scanner(roll)
    res = scanner.scan_tokens()
    assert len(res) == result + 1, roll


@pytest.mark.parametrize("roll,result", [(case.roll, case.parse_result) for case in testcases if case.parse_result])
def test_parse(roll: str, result: List[str]):
    scanner = Scanner(roll)
    tokens = scanner.scan_tokens()
    parser = Parser(tokens)
    expression = parser.parse()
    res = ASTPrinter().print(expression)
    assert res == result, roll


@pytest.mark.parametrize("roll,result", [(case.roll, case.interpret_result) for case in testcases if case.interpret_result])
def test_interpret(roll: str, result: List[Any]):
    scanner = Scanner(roll)
    parser = Parser(scanner.scan_tokens())
    expression = parser.parse()
    res = Interpreter().interpret(expression)
    res = Interpreter().interpret(expression, average=True)
    assert res == result, roll
