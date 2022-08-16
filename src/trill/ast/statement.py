"""Statements."""
from dataclasses import dataclass
from typing import List, Union

from . import expression
from .base import T, Visitor, Node
from ..tokens import Token


class StatementVisitor(Visitor[T]):
    ...


@dataclass
class Statement(Node):
    ...


@dataclass
class Expression(Statement):
    expression: expression.Expression


@dataclass
class Variable(Statement):
    name: Token
    initializer: expression.Expression


@dataclass
class Block(Statement):
    statements: List[Statement]


@dataclass
class Foreach(Statement):
    iterator: expression.Variable
    source: expression.Expression
    block: Union[Block, expression.Expression]
