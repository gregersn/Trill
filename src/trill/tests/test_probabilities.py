"""Test calculating probabilities."""

from typing import Dict, Optional
import pytest

from trill.calculator import Calculator
from trill.parser import Parser
from trill.tokenizer import Tokenizer

from trill.tests.probability_cases import testcases


@pytest.mark.parametrize(
    "roll,distribution,average,spread,mean_deviation",
    [(case.roll, case.distribution, case.average, case.spread, case.mean_deviation) for case in testcases],
)
def test_probabilities(
    roll: str,
    distribution: Dict[int, float],
    average: Optional[float],
    spread: Optional[float],
    mean_deviation: Optional[float],
):
    scanner = Tokenizer(roll)
    parser = Parser(scanner.scan_tokens())
    expression = parser.parse()
    res = Calculator().interpret(expression)

    dist, avg, spr, mean_dev = res

    for k, v in dist.items():
        # Multiplied by a hundred because  the tests were first written in percentage
        # and this is easier than updateing the values in the tests.
        assert round(v * 100, 3) == distribution[k]

    if average is not None:
        assert avg is not None
        assert round(avg, 11) == average

    if spread is not None:
        assert spr is not None
        assert round(spr, 11) == spread

    if mean_deviation is not None:
        assert mean_dev is not None
        assert round(mean_dev, 12) == mean_deviation
