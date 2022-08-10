"""Troll reserved keywords."""
from .tokens import TokenType

KEYWORDS = {
    'choose': TokenType.CHOOSE,
    'count': TokenType.COUNT,
    'different': TokenType.DIFFERENT,
    'drop': TokenType.DROP,
    'keep': TokenType.KEEP,
    'max': TokenType.MAX,
    'maximal': TokenType.MAXIMAL,
    'median': TokenType.MEDIAN,
    'min': TokenType.MIN,
    'minimal': TokenType.MINIMAL,
    'mod': TokenType.MODULO,
    'pick': TokenType.PICK,
    'sgn': TokenType.SIGN,
    'sum': TokenType.SUM,
}
