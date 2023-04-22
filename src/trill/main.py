"""Run Trill dice roller."""
from pathlib import Path
from typing import Optional
import typer
from .tokens import TokenType
from .tokenizer import Token, Tokenizer
from .interpreter import Interpreter
from .parser import Parser
from .ast.printer import ASTPrinter
from .ast.expression import Binary, Grouping, Literal, Unary
from .error import handler as error_handler

app = typer.Typer(add_completion=False)


def main():
    """Main function."""
    expression = Binary(
        Unary(Token(TokenType.MINUS, '-', None, 1, 1), Literal(123)),
        Token(TokenType.MULTIPLY, '*', None, 1, 2),
        Grouping(Literal(45.67)),
    )

    ASTPrinter().print([expression])


@app.command()
def run(
        source: str = typer.Argument(..., help="Source of dice rolls."),
        average: bool = typer.Option(False, help="Use average dice values."),
        seed: Optional[int] = typer.Option(None, help="Set random seed.")
):
    """
    Use SOURCE to roll dice according to the Troll language.
    If SOURCE resolves to an existing file, it will be read and used.
    """
    if Path(source).exists():
        with open(Path(source), 'r', encoding="utf-8") as f:
            source = f.read()

    tokens = Tokenizer(source).scan_tokens()
    parsed = Parser(tokens).parse()
    result = Interpreter(seed).interpret(parsed, average=average)

    if error_handler.had_error:
        for error in error_handler.error_report:
            print(error)
        return

    for line in result:
        print(line)

if __name__ == '__main__':
    main()
