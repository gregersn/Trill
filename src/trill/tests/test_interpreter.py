"""Test miscellanous Troll rolls."""
from typing import Any, List

import pytest

from trill.interpreter import Interpreter
from trill.parser import Parser
from trill.tokenizer import Tokenizer

from trill.tests.cases import testcases


@pytest.mark.parametrize("roll,result", [(case.roll, case.interpret_result) for case in testcases if case.interpret_result])
def test_interpret(roll: str, result: List[Any]):
    scanner = Tokenizer(roll)
    parser = Parser(scanner.scan_tokens())
    expression = parser.parse()
    res = Interpreter().interpret(expression)
    res = Interpreter().interpret(expression, average=True)
    assert res == result, roll
