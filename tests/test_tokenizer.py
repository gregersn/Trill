from troll.tokenizer import Scanner
from troll.tokens import TokenType
from troll.error import had_error

from typing import List


def test_roll_one():
    scanner = Scanner("d6")
    res = scanner.scan_tokens()

    assert not had_error 

    assert len(res) == 3
    assert res[0].token_type == TokenType.DICE
    assert res[1].token_type == TokenType.NUMBER
    assert res[1].literal == 6 
    assert res[2].token_type == TokenType.EOF

def test_roll_multiple():
    scanner = Scanner("3d6")
    res = scanner.scan_tokens()

    assert not had_error 

    assert len(res) == 4
    assert res[0].token_type == TokenType.NUMBER
    assert res[1].token_type == TokenType.DICE
    assert res[2].token_type == TokenType.NUMBER

def test_roll_multiple_calculated():
    scanner = Scanner("(4+1)d6")
    res = scanner.scan_tokens()

    assert not had_error 

    assert len(res) == 8
    types = [TokenType.LPAREN, TokenType.NUMBER, TokenType.PLUS, TokenType.NUMBER, TokenType.RPAREN, TokenType.DICE, TokenType.NUMBER]

    for token, type in zip(res, types):
        assert  token.token_type == type

