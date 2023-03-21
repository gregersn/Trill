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

    def visit_Block_Expression(self, expr: expression.Block) -> str:
        return f'(block {"; ".join(self.print(expr.statements))})'

    def visit_Literal_Expression(self, expr: expression.Literal) -> str:
        return str(expr.value)

    def visit_Assign_Expression(self, expr: expression.Assign) -> str:
        return self.parenthesize(f'assign {expr.name.literal}', expr.value)

    def visit_Variable_Expression(self, expr: expression.Variable) -> str:
        return expr.name.lexeme

    def visit_Pair_Expression(self, expr: expression.Pair) -> str:
        return self.parenthesize('pair', expr.first, expr.second)

    def visit_List_Expression(self, expr: expression.List) -> str:
        return f'(collection {" ".join([self.evaluate(v) for v in expr.value])})'

    def visit_Conditional_Expression(self, stmt: expression.Conditional) -> str:
        return self.parenthesize('if', stmt.condition, stmt.truth, stmt.falsy)

    def visit_Foreach_Expression(self, expr: expression.Foreach):
        return self.parenthesize('foreach', expr.iterator, expr.source, expr.block)

    def visit_Repeat_Expression(self, stmt: expression.Repeat):
        return self.parenthesize(f'repeat {stmt.condition.literal}', stmt.action, stmt.qualifier)

    def visit_Accumulate_Expression(self, stmt: expression.Accumulate):
        return self.parenthesize('accumulate', stmt.action, stmt.qualifier)

    def visit_Call_Expression(self, expr: expression.Call):
        return self.parenthesize(f"call {expr.name.literal}", *expr.parameters)

    def visit_Function_Statement(self, stmt: statement.Function):
        name = stmt.name
        parameters = stmt.parameters
        expr = stmt.expression

        return self.parenthesize(f"function {name.literal} ({','.join(p.literal for p in parameters)})", expr)

    def visit_Compositional_Statement(self, stmt: statement.Compositional):
        name = stmt.name
        empty = stmt.empty
        singleton = stmt.singleton
        union = stmt.union

        return self.parenthesize(f"compositional {name.literal} {empty.value} {singleton.literal} {union.literal}")

    def visit_Print_Statement(self, stmt: statement.Print):
        repeats = stmt.repeats
        expr = stmt.expression

        return self.parenthesize(f"textbox {repeats}", expr)

    def visit_TextAlign_Expression(self, expr: expression.TextAlign):
        return self.parenthesize('textalign', expr.left, expr.right)
