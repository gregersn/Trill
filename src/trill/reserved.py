"""Troll reserved keywords."""
from .tokens import TokenType

KEYWORDS = {
    'mod': TokenType.MODULO,
    'sgn': TokenType.SIGN,
    'sum': TokenType.SUM,
    'count': TokenType.COUNT,
    'choose': TokenType.CHOOSE,
    'pick': TokenType.PICK,
    'min': TokenType.MIN,
    'max': TokenType.MAX,
    'minimal': TokenType.MINIMAL,
    'maximal': TokenType.MAXIMAL,
    'drop': TokenType.DROP,
    'keep': TokenType.KEEP,
}
