"""Run Troll dice rolling."""
from .tokens import TokenType
from .tokenizer import Token, Scanner
from .interpreter import Interpreter
from .parser import Parser
from .ast.printer import ASTPrinter
from .ast.expression import Binary, Grouping, Literal, Unary


def main():
    """Main function."""
    expression = Binary(
        Unary(Token(TokenType.MINUS, '-', None, 1), Literal(123)),
        Token(TokenType.MULTIPLY, '*', None, 1),
        Grouping(Literal(45.67)),
    )

    ASTPrinter().print(expression)


def run(source: str):
    tokens = Scanner(source).scan_tokens()
    parsed = Parser(tokens).parse()
    result = Interpreter().interpret(parsed)
    print(result)


if __name__ == '__main__':
    main()
