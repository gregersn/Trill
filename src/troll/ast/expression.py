from dataclasses import dataclass
from typing import Any
from ..tokens import Token

from .base import T, Visitor

class ExpressionVisitor(Visitor[T]):
    ...

class Expression:
    def accept(self, visitor: ExpressionVisitor[Any]):
        method_name = 'visit_' + type(self).__name__ + '_' + type(self).__bases__[0].__name__
        visitor_function = getattr(visitor, method_name)
        return visitor_function(self)

@dataclass
class Binary(Expression):
    left: Expression
    operator: Token
    right: Expression

@dataclass
class Grouping(Expression):
    expression: Expression

@dataclass
class Literal(Expression):
    value: Any

@dataclass
class Unary(Expression):
    operator: Token
    right: Expression


