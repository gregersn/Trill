"""Statements."""
from dataclasses import dataclass
from typing import Any, List

from .base import T, Visitor, Node
from ..tokens import Token


class StatementVisitor(Visitor[T]):
    ...


@dataclass
class Statement(Node):
    ...


@dataclass
class Function(Statement):
    name: Token
    parameters: List[Token]
    expression: Statement


@dataclass
class Print(Statement):
    expression: Any
    repeats: int = 1
