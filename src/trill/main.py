"""Run Trill dice roller."""
from pathlib import Path
from typing import Optional
import typer

from .tokens import TokenType
from .tokenizer import Token, Tokenizer
from .interpreter import Interpreter
from .calculator import Calculator
from .parser import Parser
from .ast.printer import ASTPrinter
from .ast.expression import Binary, Grouping, Literal, Unary
from .error import handler as error_handler

app = typer.Typer(add_completion=False)


def main():
    """Main function."""
    expression = Binary(
        Unary(Token(TokenType.MINUS, "-", None, 1, 1), Literal(123)),
        Token(TokenType.MULTIPLY, "*", None, 1, 2),
        Grouping(Literal(45.67)),
    )

    ASTPrinter().print([expression])


@app.command()
def run(
    source: str = typer.Argument(..., help="Source of dice rolls."),
    average: bool = typer.Option(False, help="Use average dice values."),
    seed: Optional[int] = typer.Option(None, help="Set random seed."),
    probabilities: bool = typer.Option(False, help="Calculate probabilities."),
    digits: int = typer.Option(3, help="Number of digits in probabilities."),
    multiplier: int = typer.Option(100, help="Use 100 for percent (default)."),
):
    """
    Use SOURCE to roll dice according to the Troll language.
    If SOURCE resolves to an existing file, it will be read and used.
    """
    if Path(source).exists():
        with open(Path(source), "r", encoding="utf-8") as f:
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

    if probabilities:
        from rich.console import Console
        from rich.table import Table
        from rich.bar import Bar

        histogram, roll_average, spread, mean_deviation = Calculator().interpret(parsed)
        total = 1.0

        table = Table(title="Probabilities")

        table.add_column("Value", justify="right")
        if multiplier == 100:
            table.add_column("% =", justify="right")
            table.add_column("% ≥", justify="right")
        else:
            table.add_column(f"x{multiplier} =", justify="right")
            table.add_column(f"x{multiplier} ≥", justify="right")

        table.add_column("Probability graph")

        for value, chance in dict(sorted(histogram.items())).items():
            if isinstance(value, tuple):
                value = " ".join(str(x) for x in value)

            table.add_row(
                f"{value}",
                f"{round(chance * multiplier, digits):.{digits}f}",
                f"{round(total  * multiplier, digits):.{digits}f}",
                Bar(1, 0, chance),
            )

            total -= chance

        console = Console()
        console.print(table)
        if roll_average:
            console.print(f"Average: {roll_average}")
        if spread:
            console.print(f"Spread: {spread}")
        if mean_deviation:
            console.print(f"Mean deviation: {mean_deviation}")


if __name__ == "__main__":
    main()
