"""Troll reserved keywords."""
from .tokens import TokenType

KEYWORDS = {
    'mod': TokenType.MODULO,
    'sgn': TokenType.SIGN,
    'sum': TokenType.SUM,
    'count': TokenType.COUNT,
}
