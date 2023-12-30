"""Probability calculator for Trill."""
import itertools
import math
from typing import Any, ChainMap, Dict, List, Optional, TypeVar, Union
from trill import functions

from trill.tokens import TokenType
from trill.types import Number, NumberList

from .ast import expression, statement

T = TypeVar("T")


class Calculator(expression.ExpressionVisitor[T], statement.StatementVisitor[T]):
    variables: ChainMap[str, Union[Number, NumberList, str]] = ChainMap({})
    functions: Dict[str, Union[statement.Function, statement.Compositional]] = {}

    average: bool = False

    def interpret(
        self,
        statements: List[Union[expression.Expression, statement.Statement]],
        average: bool = False,
    ):
        distribution: Dict[int, float] = {}
        average_value: Optional[float] = None
        spread: Optional[float] = None
        mean_deviation: Optional[float] = None
        self.average = average

        for stmt in statements:
            if isinstance(stmt, statement.Function):
                distribution = stmt.accept(self)

        # Run statements, skip function declarations, as they are already done.
        for stmt in statements:
            if isinstance(stmt, statement.Function):
                continue
            if isinstance(stmt, statement.Statement):
                _, distribution = stmt.accept(self)
            if isinstance(stmt, expression.Expression):
                _, distribution = stmt.accept(self)

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

    def visit_Literal_Expression(self, expr: expression.Literal):
        if expr.value is None:
            raise NotImplementedError("None value not supported for Literal in statistics.")
        if isinstance(expr.value, str):
            raise NotImplementedError("String value not supported for calculation.")

        return expr.value, {expr.value: 1}

    def visit_Unary_Expression(self, expr: expression.Unary):
        token_type = expr.operator.token_type

        right, right_probabilities = expr.right.accept(self)

        if token_type == TokenType.DICE:
            start = 0 if expr.operator.lexeme == "z" else 1

            if self.average:
                res = functions.dice_average(right, 1, start)[0]
            else:
                res = functions.dice_roll(right, 1, start)[0]

            probs = functions.dice_probabilities(right, expr.operator.lexeme == "z")

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

        left_probabilities: Dict[int, Union[float, int]]

        left_value, left_probabilities = expr.left.accept(self)
        right_value, right_probabilities = expr.right.accept(self)

        if token_type in functions.COLLECTION_TOKENS:
            return functions.collection_probabilities(token_type, left_value, right_value, right_probabilities)

        left = self.variables.get(left_value, left_value) if isinstance(left_value, str) else left_value
        right = self.variables.get(right_value) if isinstance(right_value, str) else right_value

        if token_type == TokenType.DICE:
            start = 0 if expr.operator.lexeme == "z" else 1

            if not (isinstance(right, int) and isinstance(left, (int, float))):
                raise TypeError(f"Dice average only support ints, got {right} and {left}")

            if self.average:
                res = functions.dice_average(right, int(left), start)

            res = functions.dice_roll(right, int(left), start)

            dice_probs = functions.dice_probabilities(right, expr.operator.lexeme == "z")

            probability_groups: Dict[int, Any] = {}
            for count in left_probabilities.keys():
                probabilities = functions.group_probabilities(count, dice_probs)
                probability_groups[count] = probabilities

            probabilities = {k: v for _, group_probs in probability_groups.items() for k, v in group_probs.items()}

            return res, probabilities

        if token_type in functions.CALC_OPERATORS:
            func = functions.CALC_OPERATORS[token_type]
            probabilities_keys = [func(a, b) for a, b in itertools.product(left_probabilities.keys(), right_probabilities.keys())]
            probabilities_values = [a * b for a, b in itertools.product(left_probabilities.values(), right_probabilities.values())]

            return (
                func(left_value, right_value),
                dict(zip(probabilities_keys, probabilities_values)),
            )

        raise functions.UnknownOperator(token_type)

    def visit_Grouping_Expression(self, expr: expression.Grouping):
        res = expr.expression.accept(self)
        return res
