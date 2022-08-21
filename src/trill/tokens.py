"""Troll tokens."""
from enum import Enum
from typing import Any


class TokenType(Enum):
    COMMENT = '\\'
    COMMA = ','
    SEMICOLON = ';'

    LBRACKET = '{'
    RBRACKET = '}'
    LPAREN = '('
    RPAREN = ')'
    LSQUARE = '['
    RSQUARE = ']'
    PAIR_VALUE = '%'

    ASSIGN = ':='
    DEFAULT = '~'

    DIVIDE = '/'
    MINUS = '-'
    MULTIPLY = '*'
    PLUS = '+'
    MODULO = 'mod'

    AND = '&'
    NOT = '!'

    EQUAL = '='
    GREATER_THAN = '>'
    GREATER_THAN_OR_EQUAL = '>='
    LESS_THAN = '<'
    LESS_THAN_OR_EQUAL = '<='
    MINUSMINUS = '--'
    NOT_EQUAL = '=/='
    SAMPLES = '#'

    PROBABILITY = '?'

    FLOAT = 'float'
    INTEGER = 'integer'
    IDENTIFIER = 'identifier'
    SIGN = 'sign'

    DICE = 'dice'  # Dice that goes from 1 to N
    ZERODICE = 'zerodice'  # Dice that goes from zero to N-1

    COUNT = 'count'
    DIFFERENT = 'different'
    LARGEST = 'largest'
    LEAST = 'least'
    MAX = 'max'
    MAXIMAL = 'maximal'
    MEDIAN = 'median'
    MIN = 'min'
    MINIMAL = 'minimal'
    SUM = 'sum'

    CHOOSE = 'choose'
    DROP = 'drop'
    KEEP = 'keep'
    PICK = 'pick'
    RANGE = 'range'
    UNION = 'union'

    IF = 'if'
    THEN = 'then'
    ELSE = 'else'
    FOREACH = 'foreach'
    IN = 'in'
    DO = 'do'
    REPEAT = 'repeat'
    WHILE = 'while'
    UNTIL = 'until'
    ACCUMULATE = 'accumulate'

    FUNCTION = 'function'
    CALL = 'call'

    TEXTBOX = "'"

    EOF = 'eof'


class Token:
    token_type: TokenType
    lexeme: str
    literal: Any
    line: int
    column: int

    def __init__(self, _type: TokenType, lexeme: str, literal: Any, line: int, column: int):
        self.token_type = _type
        self.lexeme = lexeme
        self.literal = literal
        self.line = line
        self.column = column

    def __str__(self):
        literal = self.literal if self.literal is not None else ''
        return f"{self.token_type.value} {self.lexeme} {literal}"

    def __repr__(self):
        return f"<Token {self.token_type.name} {self.lexeme} ({self.line}, {self.column})>"

    def __eq__(self, o: object):
        """Check for equality based on content, ignoring position."""
        if not isinstance(o, self.__class__):
            return False

        return (self.token_type == o.token_type and self.lexeme == o.lexeme and self.literal == o.literal)
