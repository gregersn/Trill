"""Run Trill dice roller."""
import typer
from .tokens import TokenType
from .tokenizer import Token, Scanner
from .interpreter import Interpreter
from .parser import Parser
from .ast.printer import ASTPrinter
from .ast.expression import Binary, Grouping, Literal, Unary

app = typer.Typer(add_completion=False)


def main():
    """Main function."""
    expression = Binary(
        Unary(Token(TokenType.MINUS, '-', None, 1), Literal(123)),
        Token(TokenType.MULTIPLY, '*', None, 1),
        Grouping(Literal(45.67)),
    )

    ASTPrinter().print([expression])


@app.command()
def run(
        source: str = typer.Argument(...),
        average: bool = typer.Option(False, help="Use average dice values."),
):
    """
    Use SOURCE to roll dice according to the Troll language.
    """
    tokens = Scanner(source).scan_tokens()
    parsed = Parser(tokens).parse()
    result = Interpreter().interpret(parsed, average=average)
    for line in result:
        print(line)


if __name__ == '__main__':
    main()
