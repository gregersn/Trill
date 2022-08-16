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

    def visit_Block_Statement(self, expr: statement.Block) -> str:
        return f'(block {"; ".join(self.print(expr.statements))})'

    def visit_Block_Expression(self, expr: expression.Block) -> str:
        return f'(block {"; ".join(self.print(expr.statements))})'

    def visit_Literal_Expression(self, expr: expression.Literal) -> str:
        if expr.value is None:
            return "None"
        return str(expr.value)

    def visit_Assign_Expression(self, expr: expression.Assign) -> str:
        return self.parenthesize(f'assign {expr.name.literal}', expr.value)

    def visit_Variable_Expression(self, expr: expression.Variable) -> str:
        return expr.name.lexeme

    def visit_Expression_Statement(self, stmt: statement.Expression) -> str:
        return self.evaluate(stmt.expression)

    def visit_Variable_Statement(self, stmt: statement.Variable) -> str:
        return self.parenthesize(f'assign {stmt.name.literal}', stmt.initializer)

    def visit_List_Expression(self, expr: expression.List) -> str:
        return f'(collection {" ".join([self.evaluate(v) for v in expr.value])})'

    def visit_Conditional_Expression(self, stmt: expression.Conditional) -> str:
        return self.parenthesize('if', stmt.condition, stmt.truth, stmt.falsy)

    def visit_Foreach_Statement(self, stmt: statement.Foreach):
        return self.parenthesize('foreach', stmt.iterator, stmt.source, stmt.block)

    def visit_Repeat_Expression(self, stmt: expression.Repeat):
        return self.parenthesize(f'repeat {stmt.condition.literal}', stmt.action, stmt.qualifier)
    
    def visit_Accumulate_Expression(self, stmt: expression.Accumulate):
        return self.parenthesize(f'accumulate', stmt.action, stmt.qualifier)
