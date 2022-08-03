from enum import Enum
from typing import Any


class TokenType(Enum):
    # Artihmetic
    PLUS = '+'
    MINUS = '-'
    MULTIPLY = '*'
    DIVIDE = '/'
    LPAREN = '('
    RPAREN = ')'
    SAMPLES = '#'
    DICE = 'dice'  # Dice that goes from 1 to N
    ZERODICE = 'zerodice'  # Dice that goes from zero to N-1
    NUMBER = 'number'
    IDENTIFIER = 'identifier'
    UNION = 'union'
    SUM = 'sum'
    SIGN = 'sign'
    MODULO = 'mod'
    EOF = 'eof'

    EQUAL = '='
    LESS_THAN = '<'
    GREATER_THAN = '>'

    SEMICOLON = ';'


class Token:
    token_type: TokenType
    lexeme: str
    literal: Any
    line: int

    def __init__(self, _type: TokenType, lexeme: str, literal: Any, line: int):
        self.token_type = _type
        self.lexeme = lexeme
        self.literal = literal
        self.line = line

    def __str__(self):
        return f"{self.token_type.value} {self.lexeme} {self.literal}"

    def __repr__(self):
        return str(self)
