"""Statements."""
from dataclasses import dataclass
from typing import Any, List, Union

from .base import T, Visitor, Node
from ..tokens import Token
from .expression import Expression


class StatementVisitor(Visitor[T]):
    ...


@dataclass
class Statement(Node):
    ...


@dataclass
class Function(Statement):
    name: Token
    parameters: List[Token]
    expression: Union[Statement , 'Expression']


@dataclass
class Print(Statement):
    expression: Any
    repeats: int = 1
