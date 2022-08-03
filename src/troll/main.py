from .tokens import TokenType
from .tokenizer import Token
from .ast.printer import ASTPrinter
from .ast.expression import Binary, Grouping, Literal, Unary

def main():
    print("Hello")
    expression = Binary(
        Unary(
            Token(TokenType.MINUS, '-', None, 1),
            Literal(123)
        ),
        Token(TokenType.MULTIPLY, '*', None, 1),
        Grouping(Literal(45.67))
    )

    ASTPrinter().print(expression)


if __name__ == '__main__':
    main()