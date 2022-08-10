"""Troll interpreter."""
from typing import TypeVar, List, Any
import random
from .ast import expression
from .ast import statement
from .ast.base import Node
from .tokens import TokenType

T = TypeVar('T')


class Interpreter(expression.ExpressionVisitor[T], statement.StatementVisitor[T]):
    average: bool = False

    def interpret(self, exprs: List[Node], average: bool = False):
        self.average = average
        output: List[Any] = []
        for expr in exprs:
            output.append(expr.accept(self))
        return output

    def visit_Literal_Expression(self, expr: expression.Literal):
        return expr.value

    def evaluate(self, expr: expression.Expression):
        return expr.accept(self)

    def visit_Unary_Expression(self, expr: expression.Unary):
        right = self.evaluate(expr.right)

        if expr.operator.token_type == TokenType.MINUS:
            return -right

        if expr.operator.token_type == TokenType.DICE:
            start = 0 if expr.operator.lexeme == 'z' else 1
            if self.average:
                return (right + start) / 2
            else:
                return random.randint(start, right)

        if expr.operator.token_type == TokenType.SUM:
            return sum(right)

        if expr.operator.token_type == TokenType.SIGN:
            if right == 0:
                return 0
            return right / abs(right)

        if expr.operator.token_type == TokenType.COUNT:
            return len(right)

        raise Exception(f"Unknown operator {expr.operator.token_type} in unary expression")

    def visit_Binary_Expression(self, expr: expression.Binary):
        if expr.operator.token_type == TokenType.SAMPLES:
            return [self.evaluate(expr.right) for _ in range(int(self.evaluate(expr.left)))]

        left = self.evaluate(expr.left)
        right = self.evaluate(expr.right)

        if expr.operator.token_type == TokenType.DICE:
            start = 0 if expr.operator.lexeme == 'z' else 1
            if self.average:
                return [
                    (right + start) / 2,
                ] * int(left)
            else:
                return [random.randint(start, right) for _ in range(left)]

        if expr.operator.token_type == TokenType.RANGE:
            return list(range(left, right + 1))

        if expr.operator.token_type == TokenType.UNION:
            if isinstance(left, (int, float)):
                left = [left]

            if isinstance(right, (int, float)):
                right = [right]

            return left + right

        if expr.operator.token_type == TokenType.PLUS:
            return left + right

        if expr.operator.token_type == TokenType.MINUS:
            return left - right

        if expr.operator.token_type == TokenType.DIVIDE:
            return left // right

        if expr.operator.token_type == TokenType.MULTIPLY:
            return left * right

        raise Exception(f"Unknown operator {expr.operator.token_type} in binary expression")

    def visit_Grouping_Expression(self, expr: expression.Grouping):
        return self.evaluate(expr.expression)

    def visit_List_Expression(self, expr: expression.List):
        return [self.evaluate(v) for v in expr.value]

    def visit_Expression_Statement(self, stmt: statement.Expression):
        return self.evaluate(stmt.expression)
