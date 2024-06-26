"""Test helper functions."""
from trill.functions import (
    collection_operation,
    collection_probabilities,
    dice_average,
    dice_probabilities,
    dice_roll,
    group_probabilities,
)
from trill.tokens import TokenType


def test_dice_average():
    assert dice_average(6)[0] == 3.5
    assert dice_average(6, start=0)[0] == 3


def test_dice_roll():
    for sides in [4, 6, 8, 10, 12, 20, 10]:
        total = 0
        rolls = 100000
        for _ in range(rolls):
            total += dice_roll(sides)[0]

        assert (
            abs(round(total / rolls, 1) - dice_average(sides)[0]) < 0.5
        ), f"{sides} sides"

        total = 0
        rolls = 10000
        for _ in range(rolls):
            total += dice_roll(sides, start=0)[0]

        assert (
            abs(round(total / rolls, 1) - dice_average(sides, start=0)[0]) < 0.5
        ), f"{sides} sides"


def test_dice_probability():
    assert dice_probabilities(6) == {
        1: 1,
        2: 1,
        3: 1,
        4: 1,
        5: 1,
        6: 1,
    }

    assert dice_probabilities(6, True) == {
        0: 1,
        1: 1,
        2: 1,
        3: 1,
        4: 1,
        5: 1,
    }


def test_group_probabilities():
    assert group_probabilities(2, {1: 1, 2: 1}) == {
        (1, 1): 0.25,
        (1, 2): 0.5,
        (2, 2): 0.25,
    }


def test_collection_operation():
    assert collection_operation(TokenType.SAMPLES, 1, [1, 2, 3, 4]) == [1, 2, 3, 4]
    assert collection_operation(TokenType.SAMPLES, 2, [1, 2]) == [1, 2, 1, 2]

    assert collection_operation(TokenType.LARGEST, 2, [1, 2, 3, 4]) == [4, 3]
    assert collection_operation(TokenType.LEAST, 2, [1, 2, 3, 4]) == [1, 2]


def test_collection_probabilities_samples():
    assert collection_probabilities(TokenType.SAMPLES, 1, [1, 2], {1: 0.5, 2: 0.5}) == (
        [1, 2],
        {(1,): 0.5, (2,): 0.5},
    )

    assert collection_probabilities(TokenType.SAMPLES, 2, [1, 2], {1: 0.5, 2: 0.5}) == (
        [1, 2, 1, 2],
        {(1, 1): 0.25, (1, 2): 0.5, (2, 2): 0.25},
    )


def test_collection_probabilities_largest():
    assert collection_probabilities(
        TokenType.LARGEST, 2, [1, 2, 3], {(1,): 1 / 3, (2,): 1 / 3, (3,): 1 / 3}
    ) == (
        [3, 2],
        {(1,): 1 / 3, (2,): 1 / 3, (3,): 1 / 3},
    )

    assert collection_probabilities(
        TokenType.LEAST, 2, [1, 2, 3], {(1,): 1 / 3, (2,): 1 / 3, (3,): 1 / 3}
    ) == (
        [1, 2],
        {(1,): 1 / 3, (2,): 1 / 3, (3,): 1 / 3},
    )
