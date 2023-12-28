"""Functions for use by the interpreter."""
import random
from typing import Any, Iterable, List, Literal, Sequence, Union, cast
from trill.tokens import Token, TokenType

from trill.types import Number, NumberList


class UnknownOperator(Exception):
    """Unknown operator."""


def dice_roll(sides: int, count: int = 1, start: int = 1):
    return [random.randint(start, sides) for _ in range(int(count))]


def dice_average(sides: int, count: int = 1, start: int = 1):
    return [(sides + start) / 2] * count


def text_align(
    left: Union[Number, NumberList, str], right: Union[Number, NumberList, str], align_operator: Literal["|>", "<|", "<>", "||"]
):
    if isinstance(left, str):
        left = left.split("\n")

    if isinstance(right, str):
        right = right.split("\n")

    if not isinstance(left, list):
        left = [left]
    if not isinstance(right, list):
        right = [right]

    max_length_left = len(str(max(left, key=lambda x: len(str(x)))))
    max_length_right = len(str(max(right, key=lambda x: len(str(x)))))
    max_length = max(max_length_left, max_length_right)

    if align_operator == "|>":
        output = [f"{t:<{max_length}}" for t in left] + [f"{t:<{max_length}}" for t in right]
        return "\n".join(output)

    if align_operator == "<|":
        output = [f"{t:>{max_length}}" for t in left] + [f"{t:>{max_length}}" for t in right]
        return "\n".join(output)

    if align_operator == "<>":
        output = [f"{t:^{max_length}}" for t in left] + [f"{t:^{max_length}}" for t in right]
        return "\n".join(output)

    if align_operator == "||":
        max_height = max(len(left), len(right))

        left += [" " * max_length_left] * (max_height - len(left))
        right += [" " * max_length_right] * (max_height - len(right))

        preliminary = list(zip(left, right))

        return "\n".join(["".join([str(v) for v in t]) for t in preliminary])

    raise NotImplementedError(align_operator)


def unary_expression(token_type: TokenType, value: Any, operator: Token, average: bool = False):
    if token_type == TokenType.NOT:
        if not value:
            return 1
        return cast(Sequence[int], [])

    if token_type == TokenType.PAIR_VALUE:
        v = operator.literal

        return value[v - 1]

    if token_type == TokenType.MINUS:
        return -value

    if token_type == TokenType.DICE:
        start = 0 if operator.lexeme == "z" else 1

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
    token_type: Literal[TokenType.SAMPLES, TokenType.LARGEST, TokenType.LEAST],
    count: int,
    collection: Sequence,
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

    if token_type == TokenType.LARGEST:
        return list(sorted(collection))[-count:]

    if token_type == TokenType.LEAST:
        return list(sorted(collection))[:-count]

    raise NotImplementedError(token_type)
