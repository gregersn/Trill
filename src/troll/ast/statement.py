from dataclasses import dataclass

from troll.ast import expression
from .base import T, Visitor, Node


class StatementVisitor(Visitor[T]):
    ...


class Statement(Node):
    ...


@dataclass
class Expression(Statement):
    expression: expression.Expression
