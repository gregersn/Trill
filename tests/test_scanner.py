"""Test that the scanner handles miscellanous stuff."""
import pytest
from trill.tokenizer import Scanner
from trill.tokens import TokenType, Token

number_tests = [
    ('4', Token(TokenType.INTEGER, '4', 4, 0, 1)),
    ('3.141', Token(TokenType.FLOAT, '3.141', 3.141, 0, 1)),
]


@pytest.mark.parametrize("source,result", number_tests)
def test_numbers(source: str, result: Token):
    scanner = Scanner(source)
    tokens = scanner.scan_tokens()
    assert tokens[0] == result


identifier_tests = [
    ('foo', Token(TokenType.IDENTIFIER, 'foo', 'foo', 0, 1)),
]


@pytest.mark.parametrize("source,result", number_tests)
def test_identifiers(source: str, result: Token):
    scanner = Scanner(source)
    tokens = scanner.scan_tokens()
    assert tokens[0] == result
