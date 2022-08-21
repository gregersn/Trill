"""Troll tokenizer."""
from typing import Any, List

from .tokens import TokenType
from .tokens import Token
from .error import handler as error_handler, ScannerError
from .reserved import KEYWORDS


class Scanner:
    source: str
    tokens: List[Token]

    _start: int = 0
    _current: int = 0
    _line: int = 1
    _column: int = 0

    def __init__(self, source: str):
        self.source = source
        error_handler.reset()

    def scan_tokens(self) -> List[Token]:
        self.tokens = []
        while not self.is_at_end():
            self._start = self._current
            self.scan_token()

        self.tokens.append(Token(TokenType.EOF, "\\0", None, self._line, self._current))
        return self.tokens

    def number(self):
        """Scan numbers."""

        is_float = False

        while self.peek().isdigit():
            self.advance()

        if self.peek() == '.' and self.peek_next().isdigit():
            is_float = True
            self.advance()

            while self.peek().isdigit():
                self.advance()

        if is_float:
            self.add_token(TokenType.FLOAT, float(self.source[self._start:self._current]))
        else:
            self.add_token(TokenType.INTEGER, int(self.source[self._start:self._current], 10))

    def identifier(self):
        """Identifiers are either custom names or reserved keywords."""
        while self.peek().isalpha():
            self.advance()

        text = self.source[self._start:self._current]
        _type = KEYWORDS.get(text, TokenType.IDENTIFIER)
        self.add_token(_type, text)

    def scan_token(self):
        """Scan for the next token."""

        character = self.advance()
        if character == '<':
            if self.peek() == '=':
                self.advance()
                return self.add_token(TokenType.LESS_THAN_OR_EQUAL, '<=')
            return self.add_token(TokenType.LESS_THAN, '<')

        if character == "'":
            return self.add_token(TokenType.TEXTBOX, "'")

        if character == '>':
            if self.peek() == '=':
                self.advance()
                return self.add_token(TokenType.GREATER_THAN_OR_EQUAL, '>=')
            return self.add_token(TokenType.GREATER_THAN, '>')

        if character == ':' and self.peek() == '=':
            self.advance()
            return self.add_token(TokenType.ASSIGN, ':=')

        if character == '=':
            if self.peek() == '/' and self.peek_next() == '=':
                self.advance()
                self.advance()
                return self.add_token(TokenType.NOT_EQUAL, '=/=')
            return self.add_token(TokenType.EQUAL, '=')

        if character == ';':
            return self.add_token(TokenType.SEMICOLON, character)

        if character == '+':
            return self.add_token(TokenType.PLUS, character)

        if character == '/':
            return self.add_token(TokenType.DIVIDE, character)

        if character == '\\':
            self.comment()
            return

        if character == '*':
            return self.add_token(TokenType.MULTIPLY, character)

        if character == '?':
            return self.add_token(TokenType.PROBABILITY, character)

        if character == '&':
            return self.add_token(TokenType.AND, character)

        if character == '!':
            return self.add_token(TokenType.NOT, character)

        if character == '~':
            return self.add_token(TokenType.DEFAULT, character)

        if character == '-':
            if self.peek() == '-':
                self.advance()
                return self.add_token(TokenType.MINUSMINUS, '--')
            return self.add_token(TokenType.MINUS, character)

        if character == '(':
            return self.add_token(TokenType.LPAREN, character)

        if character == ')':
            return self.add_token(TokenType.RPAREN, character)

        if character == '{':
            return self.add_token(TokenType.LBRACKET, character)

        if character == '}':
            return self.add_token(TokenType.RBRACKET, character)

        if character == '[':
            return self.add_token(TokenType.LSQUARE, character)

        if character == ']':
            return self.add_token(TokenType.RSQUARE, character)

        if character == ',':
            return self.add_token(TokenType.COMMA, character)

        if character == '%' and self.peek().isdigit():
            element = int(self.advance(), 10)
            if element not in [1, 2]:
                error_handler.report(ScannerError(self._line, self._column, f"{element} is not a pair value"))
                return
            return self.add_token(TokenType.PAIR_VALUE, element)

        if character == '#':
            return self.add_token(TokenType.SAMPLES, character)

        if character in ('U', '@'):
            return self.add_token(TokenType.UNION, character)

        if character == '.' and self.peek() == '.':
            self.advance()
            return self.add_token(TokenType.RANGE, '..')

        if (character.lower() == 'd' or character.lower() == 'z') and not self.peek().isalpha():
            return self.add_token(TokenType.DICE, character)

        if character in [' ', '\t', '\r']:
            return

        if character == '\n':
            self._line += 1
            self._column = 0
            return

        if character.isdigit():
            return self.number()

        if character.isalpha():
            return self.identifier()

        error_handler.report(ScannerError(self._line, self._column, f"Unexpected character: {character}"))

    def is_at_end(self):
        return self._current >= len(self.source)

    def advance(self):
        self._current += 1
        self._column += 1
        return self.source[self._current - 1]

    def comment(self):
        res = ''

        self.advance()
        while self.peek() != '\n':
            res += self.advance()
        return res

    def peek(self):
        if self.is_at_end():
            return '\0'

        return self.source[self._current]

    def peek_next(self):
        if self._current + 1 >= len(self.source):
            return '\0'
        return self.source[self._current + 1]

    def add_token(self, _type: TokenType, literal: Any = None):
        text = self.source[self._start:self._current]
        self.tokens.append(Token(_type, text, literal, self._line, self._start))
