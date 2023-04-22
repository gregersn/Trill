"""Base AST classes and types."""
import sys
from dataclasses import dataclass
import random
from typing import Any, Optional, TypeVar, Generic

T = TypeVar('T')


class UnknownNodeType(Exception):
    """Unknown node type."""


class Visitor(Generic[T]):
    """Visitor base class."""

    def __init__(self, seed: Optional[int] = None):
        if seed is None:
            seed = random.randrange(sys.maxsize)
        random.seed(seed)

    def visit_generic(self, node: 'Node'):
        """Visit a generic node."""
        raise UnknownNodeType(f"No visit_{type(node).__name__} method")


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
