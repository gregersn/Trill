"""A Parser that prints the AST tree."""
from typing import List

from .base import Node
from . import expression
from . import statement


class ASTPrinter(expression.ExpressionVisitor[str], statement.StatementVisitor[str]):

    def print(self, exprs: List[Node]):
        output: List[str] = []
        for expr in exprs:
            output.append(str(expr.accept(self)))
        return output

    def parenthesize(self, name: str, *exprs: expression.Expression):
        output: List[str] = []

        output.append(f"({name}")
        for expr in exprs:
            output.append(" ")
            output.append(str(expr.accept(self)))
        output.append(")")

        return "".join(output)

    def evaluate(self, expr: expression.Expression):
        return expr.accept(self)

    def visit_Binary_Expression(self, expr: expression.Binary) -> str:
        return self.parenthesize(expr.operator.lexeme, expr.left, expr.right)

    def visit_Unary_Expression(self, expr: expression.Unary) -> str:
        return self.parenthesize(expr.operator.lexeme, expr.right)

    def visit_Grouping_Expression(self, expr: expression.Grouping) -> str:
        return self.parenthesize('group', expr.expression)

    def visit_Literal_Expression(self, expr: expression.Literal) -> str:
        if expr.value is None:
            return "None"
        return str(expr.value)

    def visit_Expression_Statement(self, stmt: statement.Expression) -> str:
        return self.evaluate(stmt.expression)
