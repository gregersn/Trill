from typing import List

from . import expression
from . import statement

class ASTPrinter(expression.ExpressionVisitor[str], statement.StatementVisitor[str]):
    def print(self, exprs: List[expression.Expression]):
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

    def evaluate(self, expression: expression.Expression):
        return expression.accept(self)

    def visit_Binary_Expression(self, expression: expression.Binary) -> str:
        return self.parenthesize(expression.operator.lexeme, expression.left, expression.right)
    
    def visit_Unary_Expression(self, expression: expression.Unary) -> str:
        return self.parenthesize(expression.operator.lexeme, expression.right)
    
    def visit_Grouping_Expression(self, expr: expression.Grouping) -> str:
        return self.parenthesize('group', expr.expression)
    
    def visit_Literal_Expression(self, expression: expression.Literal) -> str:
        if expression.value is None:
            return "None"
        return str(expression.value)

    def visit_Expression_Statement(self, stmt: statement.Expression) -> str:
        return self.evaluate(stmt.expression)
