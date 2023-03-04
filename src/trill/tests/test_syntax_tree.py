"""Syntax tree tests."""
from trill.tokens import TokenType
from trill.tokenizer import Token
from trill.ast.printer import ASTPrinter
from trill.ast.expression import Binary, Grouping, Literal, Unary


def test_printer():
    expression = [
        Binary(
            Unary(Token(TokenType.MINUS, '-', None, 1, 1), Literal(123)),
            Token(TokenType.MULTIPLY, '*', None, 1, 1),
            Grouping(Literal(45.67)),
        ),
    ]

    res = ASTPrinter().print(expression)
    assert res == ["(* (- 123) (group 45.67))"]
