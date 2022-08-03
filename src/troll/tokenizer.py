from typing import Any, List
from troll.tokens import TokenType
from .tokens import Token
from .error import error
from .reserved import KEYWORDS


class Scanner:
    source: str
    tokens: List[Token]

    _start: int = 0
    _current: int = 0
    _line: int = 1

    def __init__(self, source: str):
        self.source = source

    def scan_tokens(self) -> List[Token]:
        self.tokens = []
        while not self.is_at_end():
            self._start = self._current
            self.scan_token()

        self.tokens.append(Token(TokenType.EOF, "", None, self._line))
        return self.tokens

    def number(self):
        while self.peek().isdigit():
            self.advance()

        if self.peek() == '.' and self.peek_next().isdigit():
            self.advance()

            while self.peek().isdigit():
                self.advance()

        self.add_token(TokenType.NUMBER, int(self.source[self._start:self._current], 10))

    def identifier(self):
        while self.peek().isalpha() or self.peek().isdigit():
            self.advance()

        text = self.source[self._start:self._current]
        _type = KEYWORDS.get(text)
        if _type is None:
            _type = TokenType.IDENTIFIER

        self.add_token(_type)

    def scan_token(self):
        character = self.advance()
        if character == '+':
            return self.add_token(TokenType.PLUS)

        if character == '/':
            return self.add_token(TokenType.DIVIDE)

        if character == '*':
            return self.add_token(TokenType.MULTIPLY)

        if character == '-':
            return self.add_token(TokenType.MINUS)

        if character == '(':
            return self.add_token(TokenType.LPAREN)

        if character == ')':
            return self.add_token(TokenType.RPAREN)

        if character == '#':
            return self.add_token(TokenType.SAMPLES)

        if character == 'U':
            return self.add_token(TokenType.UNION)

        if character.lower() == 'd' or character.lower() == 'z':
            return self.add_token(TokenType.DICE, character)

        if character == ' ':
            return

        if character == '\n':
            self._line += 1
            return

        if character.isdigit():
            return self.number()

        if character.isalpha():
            return self.identifier()

        error(self._line, f"Unexpected character: {character}")

    def is_at_end(self):
        return self._current >= len(self.source)

    def advance(self):
        self._current += 1
        return self.source[self._current - 1]

    def match(self, expected: str):
        if self.is_at_end():
            return False

        if self.source[self._current] != expected:
            return False

        self._current += 1
        return True

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
        self.tokens.append(Token(_type, text, literal, self._line))
