"""Probability test cases."""

from dataclasses import dataclass
from typing import Dict, Sequence, Tuple, Union


@dataclass
class TestCase:
    roll: str
    distribution: Dict[Union[int, Tuple[int, ...]], float]
    average: Union[float, None] = None
    spread: Union[float, None] = None
    mean_deviation: Union[float, None] = None


testcases: Sequence[TestCase] = [
    TestCase("5", {5: 100.0}, 5.0, 0.0, 0.0),
    TestCase(
        "d6",
        {1: 16.667, 2: 16.667, 3: 16.667, 4: 16.667, 5: 16.667, 6: 16.667},
        3.5,
        1.70782512766,
        1.5,
    ),
    TestCase(
        "d6 + 3",
        {
            4: 16.667,
            5: 16.667,
            6: 16.667,
            7: 16.667,
            8: 16.667,
            9: 16.667,
        },
        6.5,
        1.70782512766,
        1.5,
    ),
    TestCase(
        "2d3",
        {
            (1, 1): 11.111,
            (1, 2): 22.222,
            (1, 3): 22.222,
            (2, 2): 11.111,
            (2, 3): 22.222,
            (3, 3): 11.111,
        },
    ),
    TestCase("(1+1)d2", {(1, 1): 25.0, (1, 2): 50.0, (2, 2): 25.0}),
    TestCase(
        "(d2)d2",
        {
            (1,): 25.0,
            (1, 1): 12.5,
            (1, 2): 25.0,
            (2,): 25.0,
            (2, 2): 12.5,
        },
    ),
    TestCase("3*d2", {3: 50.0, 6: 50.0}, 4.5, 1.5, 1.5),
    TestCase(
        "sum 2d3",
        {
            2: 11.111,
            3: 22.222,
            4: 33.333,
            5: 22.222,
            6: 11.111,
        },
        4.0,
        1.15470053838,
        0.888888888889,
    ),
    TestCase(
        "sum largest 2 3d3",
        {2: 3.704, 3: 11.111, 4: 25.926, 5: 33.333, 6: 25.926},
        4.66666666667,
        1.0886621079,
        0.913580246914,
    ),
]
