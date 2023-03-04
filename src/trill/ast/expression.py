"""Expression base code."""
from dataclasses import dataclass
from typing import Union, List as TList
from ..tokens import Token

from .base import T, Visitor, Node


class ExpressionVisitor(Visitor[T]):
    ...


@dataclass
class Expression(Node):
    ...


@dataclass
class Binary(Expression):
    left: Expression
    operator: Token
    right: Expression

@dataclass
class TextAlign(Expression):
    left: Expression
    operator: Token
    right:Expression


@dataclass
class Grouping(Expression):
    expression: Expression


@dataclass
class Block(Expression):
    statements: TList[Expression]


@dataclass
class List(Expression):
    value: TList[Expression]


@dataclass
class Pair(Expression):
    first: Expression
    second: Expression


@dataclass
class Literal(Expression):
    value: Union[int, float, str, None]


@dataclass
class Unary(Expression):
    operator: Token
    right: Expression


@dataclass
class Variable(Expression):
    name: Token


@dataclass
class Assign(Expression):
    name: Token
    value: Expression


@dataclass
class Conditional(Expression):
    condition: Expression
    truth: Expression
    falsy: Expression


@dataclass
class Repeat(Expression):
    condition: Token
    action: Assign
    qualifier: Expression


@dataclass
class Accumulate(Expression):
    action: Assign
    qualifier: Expression


@dataclass
class Call(Expression):
    name: Token
    parameters: TList['Expression']


@dataclass
class Foreach(Expression):
    iterator: Variable
    source: Expression
    block: Union[Block, Expression]
