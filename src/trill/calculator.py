"""Probability calculator for Trill."""
import itertools
import math
import random
from typing import (
    ChainMap,
    Dict,
    List,
    Optional,
    Sequence,
    Tuple,
    TypeVar,
    Union,
    cast,
)

from trill.tokens import TokenType
from trill.types import Number, NumberList

from .ast import expression, statement

T = TypeVar("T")


def dice_probabilities(sides: int, z: bool = False):
    start = 0 if z else 1

    return {k: 1 for k in range(start, sides + start)}


class Calculator(expression.ExpressionVisitor[T], statement.StatementVisitor[T]):
    variables: ChainMap[str, Union[Number, NumberList, str]] = ChainMap({})
    functions: Dict[str, Union[statement.Function, statement.Compositional]] = {}

    average: bool = False

    def interpret(
        self,
        statements: List[Union[expression.Expression, statement.Statement]],
        average: bool = False,
    ):
        distribution: Dict[Union[int, float], float] = {}
        average_value = None
        spread = None
        mean_deviation = None
        self.average = average

        for stmt in statements:
            if isinstance(stmt, statement.Function):
                distribution = self.execute(stmt)

        # Run statements, skip function declarations, as they are already done.
        for stmt in statements:
            if isinstance(stmt, statement.Function):
                continue
            if isinstance(stmt, statement.Statement):
                _, distribution = self.execute(stmt)
            if isinstance(stmt, expression.Expression):
                _, distribution = self.evaluate(stmt)

        value_types = set(type(k) for k in distribution.keys())

        if value_types.issubset(set([float, int])):
            total_key = sum((a * b) for a, b in zip(distribution.keys(), distribution.values()))
            total_value = sum(distribution.values())

            average_value = total_key / total_value

            x_2 = sum((a * a * b / total_value) for a, b in zip(distribution.keys(), distribution.values()))

            spread = math.sqrt(x_2 - average_value**2)

            mean_deviation = sum(abs(k - average_value) * v for k, v in distribution.items()) / total_value

        return (
            {k: v / sum(distribution.values()) for k, v in distribution.items()},
            average_value,
            spread,
            mean_deviation,
        )

    def execute(self, stmt: statement.Statement):
        return stmt.accept(self)

    def evaluate(self, expr: expression.Expression):
        if isinstance(expr, (expression.Literal, expression.Unary, expression.Binary)):
            return expr.accept(self)

        if isinstance(expr, expression.Grouping):
            return expr.accept(self)

        raise NotImplementedError(expr)

    def visit_Literal_Expression(self, expr: expression.Literal):
        if expr.value is None:
            raise NotImplementedError("None value not supported for Literal in statistics.")
        if isinstance(expr.value, str):
            raise NotImplementedError("String value not supported for calculation.")

        return expr.value, {expr.value: 1}

    def visit_Unary_Expression(self, expr: expression.Unary):
        token_type = expr.operator.token_type

        right, right_probabilities = self.evaluate(expr.right)

        if token_type == TokenType.DICE:
            assert isinstance(right, int)
            start = 0 if expr.operator.lexeme == "z" else 1

            if self.average:
                res = (right + start) / 2

            else:
                res = random.randint(start, right)

            probs = dice_probabilities(right, expr.operator.lexeme == "z")

            return res, probs

        if token_type == TokenType.SUM:
            probabilities: Dict[int, int] = {}
            for k, v in right_probabilities.items():
                if sum(k) in probabilities:
                    probabilities[sum(k)] += v
                else:
                    probabilities[sum(k)] = v
            if isinstance(right, (int, float)):
                right = [right]

            return sum(right), probabilities

        raise NotImplementedError(token_type)

    def visit_Binary_Expression(self, expr: expression.Binary):
        token_type = expr.operator.token_type

        left_value, left_probabilities = self.evaluate(expr.left)
        right_value, right_probabilities = self.evaluate(expr.right)

        if token_type == TokenType.LARGEST:
            count = left_value
            if count == 0:
                return cast(Sequence[int], [])
            assert isinstance(right_value, list)
            assert isinstance(count, int)
            probabilities: Dict[Tuple[int, ...], float] = {}
            for dice, chance in right_probabilities.items():
                selected_dice = tuple(sorted(dice, reverse=True))[:count]
                if selected_dice in probabilities:
                    probabilities[selected_dice] += chance
                else:
                    probabilities[selected_dice] = chance

            return list(sorted(right_value))[-count:], probabilities

        if isinstance(expr.left, expression.Literal):
            val = left_value
            if isinstance(val, str):
                left = self.variables.get(val)
            else:
                left = val
        else:
            left = left_value

        if isinstance(expr.right, expression.Literal):
            val = right_value
            if isinstance(val, str):
                right = self.variables.get(val)
            else:
                right = val
        else:
            right = right_value

        if token_type == TokenType.DICE:
            start = 0 if expr.operator.lexeme == "z" else 1
            assert isinstance(right, (int))
            assert isinstance(left, (int))
            if self.average:
                res = [(right + start) / 2] * int(left)

            res = [random.randint(start, right) for _ in range(int(left))]
            dice_probs = dice_probabilities(right, expr.operator.lexeme == "z")

            probability_groups = {}
            for count in left_probabilities.keys():
                combinations = list(sorted([tuple(sorted(x)) for x in itertools.product(dice_probs.keys(), repeat=count)]))
                groups = itertools.groupby(combinations)
                probabilities = {k: v / len(combinations) for k, v in ((x, sum(1 for _ in y)) for x, y in groups)}
                probability_groups[count] = probabilities

            probabilities = {k: v for _, group_probs in probability_groups.items() for k, v in group_probs.items()}

            return res, probabilities

        if token_type in [
            TokenType.MULTIPLY,
            TokenType.PLUS,
            TokenType.MINUS,
            TokenType.DIVIDE,
        ]:

            def op_multiply(a: int, b: int) -> int:
                return a * b

            def op_add(a: int, b: int) -> int:
                return a + b

            def op_subtract(a: int, b: int) -> int:
                return a - b

            def op_divide(a: int, b: int) -> float:
                return a / b

            operation = None

            if token_type == TokenType.MULTIPLY:
                operation = op_multiply

            if token_type == TokenType.PLUS:
                operation = op_add

            if token_type == TokenType.MINUS:
                operation = op_subtract

            if token_type == TokenType.DIVIDE:
                operation = op_divide

            assert operation is not None

            probabilities_keys = [operation(a, b) for a, b in itertools.product(left_probabilities.keys(), right_probabilities.keys())]

            probabilities_values = [a * b for a, b in itertools.product(left_probabilities.values(), right_probabilities.values())]

            return (
                operation(left_value, right_value),
                dict(zip(probabilities_keys, probabilities_values)),
            )

        raise NotImplementedError(token_type)

    def visit_Grouping_Expression(self, expr: expression.Grouping):
        res = self.evaluate(expr.expression)
        return res
