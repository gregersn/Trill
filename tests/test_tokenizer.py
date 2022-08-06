"""Test the scanner."""
from troll.tokenizer import Scanner
from troll.tokens import TokenType
from troll.error import had_error


def test_roll_one():
    scanner = Scanner("d6")
    res = scanner.scan_tokens()

    assert not had_error

    assert len(res) == 3
    assert res[0].token_type == TokenType.DICE
    assert res[1].token_type == TokenType.INTEGER
    assert res[1].literal == 6
    assert res[2].token_type == TokenType.EOF


def test_roll_multiple():
    scanner = Scanner("3d6")
    res = scanner.scan_tokens()

    assert not had_error

    assert len(res) == 4
    assert res[0].token_type == TokenType.INTEGER
    assert res[1].token_type == TokenType.DICE
    assert res[2].token_type == TokenType.INTEGER


def test_roll_multiple_calculated():
    scanner = Scanner("(4+1)d6")
    res = scanner.scan_tokens()

    assert not had_error

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
