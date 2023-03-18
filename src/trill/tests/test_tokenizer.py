"""Test the scanner."""
import pytest

from trill.tokenizer import Tokenizer
from trill.tokens import TokenType, Token
from trill.error import handler as error_handler
from trill.tests.cases import testcases


def test_roll_one():
    scanner = Tokenizer("d6")
    res = scanner.scan_tokens()

    assert not error_handler.had_error

    assert len(res) == 3
    assert res[0].token_type == TokenType.DICE
    assert res[1].token_type == TokenType.INTEGER
    assert res[1].literal == 6
    assert res[2].token_type == TokenType.EOF


def test_roll_multiple():
    scanner = Tokenizer("3d6")
    res = scanner.scan_tokens()

    assert not error_handler.had_error

    assert len(res) == 4
    assert res[0].token_type == TokenType.INTEGER
    assert res[1].token_type == TokenType.DICE
    assert res[2].token_type == TokenType.INTEGER


def test_roll_multiple_calculated():
    scanner = Tokenizer("(4+1)d6")
    res = scanner.scan_tokens()

    assert not error_handler.had_error

    assert len(res) == 8
    types = [
        TokenType.LPAREN,
        TokenType.INTEGER,
        TokenType.PLUS,
        TokenType.INTEGER,
        TokenType.RPAREN,
        TokenType.DICE,
        TokenType.INTEGER,
    ]

    for token, _type in zip(res, types):
        assert token.token_type == _type


number_tests = [
    ('4', Token(TokenType.INTEGER, '4', 4, 0, 1)),
    ('3.141', Token(TokenType.FLOAT, '3.141', 3.141, 0, 1)),
]


@pytest.mark.parametrize("source,result", number_tests)
def test_numbers(source: str, result: Token):
    scanner = Tokenizer(source)
    tokens = scanner.scan_tokens()
    assert tokens[0] == result


identifier_tests = [
    ('foo', Token(TokenType.IDENTIFIER, 'foo', 'foo', 0, 1)),
]


@pytest.mark.parametrize("source,result", number_tests)
def test_identifiers(source: str, result: Token):
    scanner = Tokenizer(source)
    tokens = scanner.scan_tokens()
    assert tokens[0] == result


@pytest.mark.parametrize("roll,result", [(case.roll, case.token_count) for case in testcases if case.token_count])
def test_tokenizer(roll: str, result: int):
    scanner = Tokenizer(roll)
    res = scanner.scan_tokens()
    assert len(res) == result + 1, roll
