from typing import TypeVar, List, Any
import random
from src.ast import expression
from src.ast import statement
from src.tokens import TokenType

T = TypeVar('T')


class Interpreter(expression.ExpressionVisitor[T], statement.StatementVisitor[T]):
    average: bool = False

    def interpret(self, exprs: List[expression.Expression], average: bool = False):
        self.average = average
        output: List[Any] = []
        for expr in exprs:
            output.append(expr.accept(self))
        return output

    def visit_Literal_Expression(self, expression: expression.Literal):
        return expression.value

    def evaluate(self, expression: expression.Expression):
        return expression.accept(self)

    def visit_Unary_Expression(self, expression: expression.Unary):
        right = self.evaluate(expression.right)

        if expression.operator.token_type == TokenType.MINUS:
            return -right

        if expression.operator.token_type == TokenType.DICE:
            start = 0 if expression.operator.lexeme == 'z' else 1
            if self.average:
                return (right + start) / 2
            else:
                return random.randint(start, right)

        if expression.operator.token_type == TokenType.SUM:
            return sum(right)

        if expression.operator.token_type == TokenType.SIGN:
            if right == 0:
                return 0
            return right / abs(right)

        raise Exception(f"Unknown operator {expression.operator.token_type} in unary expression")

    def visit_Binary_Expression(self, expression: expression.Binary):
        if expression.operator.token_type == TokenType.SAMPLES:
            return [self.evaluate(expression.right) for _ in range(int(self.evaluate(expression.left)))]

        left = self.evaluate(expression.left)
        right = self.evaluate(expression.right)

        if expression.operator.token_type == TokenType.DICE:
            start = 0 if expression.operator.lexeme == 'z' else 1
            if self.average:
                return [
                    (right + start) / 2,
                ] * int(left)
            else:
                return [random.randint(start, right) for _ in range(left)]

        if expression.operator.token_type == TokenType.UNION:
            return left + right

        if expression.operator.token_type == TokenType.PLUS:
            return left + right

        if expression.operator.token_type == TokenType.MINUS:
            return left - right

        if expression.operator.token_type == TokenType.DIVIDE:
            return left // right

        if expression.operator.token_type == TokenType.MULTIPLY:
            return left * right

        raise Exception(f"Unknown operator {expression.operator.token_type} in binary expression")

    def visit_Grouping_Expression(self, expression: expression.Grouping):
        return self.evaluate(expression.expression)

    def visit_Expression_Statement(self, stmt: statement.Expression):
        return self.evaluate(stmt.expression)