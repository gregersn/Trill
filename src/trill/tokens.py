"""Troll tokens."""
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
    LBRACKET = '{'
    RBRACKET = '}'
    SAMPLES = '#'
    COMMA = ','
    DICE = 'dice'  # Dice that goes from 1 to N
    ZERODICE = 'zerodice'  # Dice that goes from zero to N-1
    INTEGER = 'integer'
    FLOAT = 'float'

    IDENTIFIER = 'identifier'
    UNION = 'union'
    SUM = 'sum'
    SIGN = 'sign'
    COUNT = 'count'
    PICK = 'pick'
    CHOOSE = 'choose'
    MODULO = 'mod'

    MIN = 'min'
    MAX = 'max'
    MINIMAL = 'minimal'
    MAXIMAL = 'maximal'
    EOF = 'eof'

    RANGE = 'range'

    EQUAL = '='
    LESS_THAN = '<'
    GREATER_THAN = '>'
    LESS_THAN_OR_EQUAL = '<='
    GREATER_THAN_OR_EQUAL = '>='
    NOT_EQUAL = '=/='

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
        return f"{self.token_type.value} {self.lexeme} {self.literal if self.literal is not None else ''}"

    def __repr__(self):
        return f"<Token {self.token_type.value} {self.lexeme} {self.literal} {self.line}>"

    def __eq__(self, o: object):
        """Check for equality based on content, ignoring position."""
        if not isinstance(o, self.__class__):
            return False

        return (self.token_type == o.token_type and self.lexeme == o.lexeme and self.literal == o.literal)
