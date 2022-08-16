"""Base AST classes and types."""
from dataclasses import dataclass
from typing import Any, TypeVar, Generic

T = TypeVar('T')


class Visitor(Generic[T]):
    """Visitor base class."""

    def visit_generic(self, node: 'Node'):
        """Visit a generic node."""
        raise Exception(f"No visit_{type(node).__name__} method")


@dataclass
class Node:
    """Node base class."""

    def accept(self, visitor: Visitor[Any]):
        """Accept visitor."""
        method_name = 'visit_' + type(self).__name__ + '_' + type(self).__bases__[0].__name__
        visitor_function = getattr(visitor, method_name)
        return visitor_function(self)

    def __repr__(self):
        return f"<{self.__class__.__name__} />"
