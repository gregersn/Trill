from dataclasses import dataclass
from typing import Any, List, TypeVar, Generic, TYPE_CHECKING
from ..tokens import Token

T = TypeVar('T')

class Visitor(Generic[T]):
    def visit_generic(self, expression: Any):
        raise Exception(f"No visit_{type(expression).__name__} method")

