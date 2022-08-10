"""Expression base code."""
from dataclasses import dataclass
from typing import Any
from ..tokens import Token

from .base import T, Visitor, Node


class ExpressionVisitor(Visitor[T]):
    ...


class Expression(Node):
    ...


@dataclass
class Binary(Expression):
    left: Expression
    operator: Token
    right: Expression


@dataclass
class Grouping(Expression):
    expression: Expression


@dataclass
class List(Expression):
    value: Any


@dataclass
class Literal(Expression):
    value: Any


@dataclass
class Unary(Expression):
    operator: Token
    right: Expression
