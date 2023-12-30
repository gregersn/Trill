"""Functions for use by the interpreter."""
import itertools
import random
import operator
from typing import Any, Dict, Iterable, List, Sequence, Tuple, Union, cast
from trill.tokens import Token, TokenType

from trill.types import Number, NumberList

CALC_OPERATORS = {
    TokenType.PLUS: operator.add,
    TokenType.MINUS: operator.sub,
    TokenType.DIVIDE: operator.floordiv,
    TokenType.MULTIPLY: operator.mul,
}


COMPARISON_OPERATORS = {
    TokenType.LESS_THAN: operator.lt,
    TokenType.LESS_THAN_OR_EQUAL: operator.le,
    TokenType.GREATER_THAN: operator.gt,
    TokenType.GREATER_THAN_OR_EQUAL: operator.ge,
    TokenType.EQUAL: operator.eq,
    TokenType.NOT_EQUAL: operator.ne,
}

COLLECTION_TOKENS = {TokenType.SAMPLES: True, TokenType.LARGEST: True, TokenType.LEAST: True}


Probabilities = Dict[int, Union[int, float]]
GroupProbabilities = Dict[Tuple[int, ...], Union[int, float]]


class UnknownOperator(Exception):
    """Unknown operator."""


def dice_average(sides: int, count: int = 1, start: int = 1):
    return [(sides + start) / 2] * count


def dice_roll(sides: int, count: int = 1, start: int = 1):
    return [random.randint(start, sides) for _ in range(int(count))]


def dice_probabilities(sides: int, z: bool = False) -> Dict[int, Union[int, float]]:
    start = 0 if z else 1

    return {k: 1 for k in range(start, sides + start)}


def text_align(left: Union[Number, NumberList, str], right: Union[Number, NumberList, str], align_operator: str):
    left_value = left
    right_value = right

    if isinstance(left_value, str):
        left_value = left_value.split("\n")

    if isinstance(right_value, str):
        right_value = right_value.split("\n")

    if not isinstance(left_value, list):
        left_value = [left_value]
    if not isinstance(right_value, list):
        right_value = [right_value]

    max_length_left = len(str(max(left_value, key=lambda x: len(str(x)))))
    max_length_right = len(str(max(right_value, key=lambda x: len(str(x)))))
    max_length = max(max_length_left, max_length_right)

    if align_operator == "|>":
        output = [f"{t:<{max_length}}" for t in left_value] + [f"{t:<{max_length}}" for t in right_value]
        return "\n".join(output)

    if align_operator == "<|":
        output = [f"{t:>{max_length}}" for t in left_value] + [f"{t:>{max_length}}" for t in right_value]
        return "\n".join(output)

    if align_operator == "<>":
        output = [f"{t:^{max_length}}" for t in left_value] + [f"{t:^{max_length}}" for t in right_value]
        return "\n".join(output)

    if align_operator == "||":
        max_height = max(len(left_value), len(right_value))

        left_value += [" " * max_length_left] * (max_height - len(left_value))
        right_value += [" " * max_length_right] * (max_height - len(right_value))

        preliminary = list(zip(left_value, right_value))

        return "\n".join(["".join([str(v) for v in t]) for t in preliminary])

    raise NotImplementedError(align_operator)


def unary_expression(token_type: TokenType, value: Any, expression_operator: Token, average: bool = False):
    if token_type == TokenType.NOT:
        if not value:
            return 1
        return cast(Sequence[int], [])

    if token_type == TokenType.PAIR_VALUE:
        v = expression_operator.literal
        if isinstance(v, int):
            return value[v - 1]
        raise NotImplementedError(f"{v} is not valid for {TokenType.PAIR_VALUE}")

    if token_type == TokenType.MINUS:
        return -value

    if token_type == TokenType.DICE:
        start = 0 if expression_operator.lexeme == "z" else 1

        if average:
            return dice_average(value, start=start)[0]

        return dice_roll(value, start=start)[0]

    if token_type == TokenType.SUM:
        if isinstance(value, (int, float)):
            value = [value]
        return sum(value)

    if token_type == TokenType.SIGN:
        if value == 0:
            return 0

        return value / abs(value)

    if token_type == TokenType.CHOOSE:
        if average:
            return value[len(value) // 2]

        return random.choice(value)

    if token_type == TokenType.MIN:
        return min(value)

    if token_type == TokenType.MAX:
        return max(value)

    if token_type == TokenType.COUNT:
        return len(value)

    if token_type == TokenType.MINIMAL:
        min_value = min(value)
        return [
            min_value,
        ] * value.count(min_value)

    if token_type == TokenType.MAXIMAL:
        max_value = max(value)
        return [
            max_value,
        ] * value.count(max_value)

    if token_type == TokenType.MEDIAN:
        mid_point = len(value) // 2
        return list(sorted(value))[mid_point]

    if token_type == TokenType.DIFFERENT:
        return list(set(value))

    if token_type == TokenType.PROBABILITY:
        if average:
            if value < 0.5:
                val = 1.0
            else:
                val = 0.0
        else:
            val = random.random()

        if val < value:
            return 1

        return cast(List[Any], [])

    raise UnknownOperator(f"Unknown operator {token_type} in unary expression")


def collection_operation(
    token_type: TokenType,
    count: int,
    collection: Union[Sequence[Any], int],
):
    if token_type == TokenType.SAMPLES:
        output: List[Union[int, float, str]] = []

        for _ in range(int(count)):
            new_val = collection
            if isinstance(new_val, Iterable):
                output = output + list(new_val)
            else:
                output.append(new_val)
        return output

    if count == 0:
        return cast(Sequence[int], [])

    if isinstance(collection, Iterable):
        if token_type == TokenType.LARGEST:
            return list(sorted(collection))[-count:]

        if token_type == TokenType.LEAST:
            return list(sorted(collection))[:-count]

    raise NotImplementedError(token_type)


def group_probabilities(picks: int, group: Union[Probabilities, GroupProbabilities]):
    combinations = list(sorted([tuple(sorted(x)) for x in itertools.product(group, repeat=picks)]))
    groups = itertools.groupby(combinations)
    probabilities = {k: v / len(combinations) for k, v in ((x, sum(1 for _ in y)) for x, y in groups)}

    return probabilities


def collection_probabilities(
    token_type: TokenType,
    count: int,
    collection: Sequence[Any],
    prev_probabilities: Union[Probabilities, GroupProbabilities],
):
    if token_type == TokenType.SAMPLES:
        output = group_probabilities(count, prev_probabilities)
        return collection_operation(token_type, count, collection), output

    if token_type in [TokenType.LARGEST, TokenType.LEAST]:
        if count == 0:
            return cast(Sequence[int], [])

        largest = token_type == TokenType.LARGEST

        probabilities: Dict[Tuple[int, ...], float] = {}
        for dice, chance in prev_probabilities.items():
            if not isinstance(dice, tuple):
                raise TypeError("Unknon type in dice")
            selected_dice = tuple(sorted(dice, reverse=largest))[:count]
            if selected_dice in probabilities:
                probabilities[selected_dice] += chance
            else:
                probabilities[selected_dice] = chance

        return list(sorted(collection))[-count:], probabilities

    raise NotImplementedError(token_type, count, collection, prev_probabilities)
