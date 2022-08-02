from dataclasses import dataclass
from typing import Any

from src.ast import expression
from .base import T, Visitor

class StatementVisitor(Visitor[T]):
    ...

class Statement:
    def accept(self, visitor: StatementVisitor[Any]):
        method_name = 'visit_' + type(self).__name__ + '_' + type(self).__bases__[0].__name__
        visitor_function = getattr(visitor, method_name)
        return visitor_function(self)
    


@dataclass
class Expression(Statement):
    expression: expression.Expression