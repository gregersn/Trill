from troll.tokens import TokenType
from troll.tokenizer import Token
from troll.ast.printer import ASTPrinter
from troll.ast.expression import Binary, Grouping, Literal, Unary

def test_printer():
    expression = [Binary(
        Unary(
            Token(TokenType.MINUS, '-', None, 1),
            Literal(123)
        ),
        Token(TokenType.MULTIPLY, '*', None, 1),
        Grouping(Literal(45.67))
    ),]

    res = ASTPrinter().print(expression)
    assert res == ["(* (- 123) (group 45.67))"]

