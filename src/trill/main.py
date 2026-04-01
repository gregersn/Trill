"""Run Trill dice roller."""

import argparse
from pathlib import Path
from typing import Optional

from .tokenizer import Tokenizer
from .interpreter import Interpreter
from .calculator import Calculator
from .parser import Parser
from .error import handler as error_handler


def parse_args(arg_list: list[str] | None):
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=str)
    parser.add_argument("-a", "--average", default=False, action="store_true")
    parser.add_argument("-s", "--seed", type=int, default=None)
    parser.add_argument("-p", "--probabilities", default=False, action="store_true")
    parser.add_argument("-d", "--digits", type=int, default=3)
    parser.add_argument("-m", "--multiplier", type=int, default=100)

    args = parser.parse_args(arg_list)
    return args


def run(
    source: str,
    average: bool = False,
    seed: Optional[int] = None,
    probabilities: bool = False,
    digits: int = 3,
    multiplier: int = 100,
):
    """
    Use SOURCE to roll dice according to the Troll language.
    If SOURCE resolves to an existing file, it will be read and used.

    AVERAGE - Use average dice values
    SEED - Set random seed
    PROBABILITIES - Calculate probabilities
    DIGITS - Number of digits in probabilities
    MULTIPLIER - Use 100 for percent (default)
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
        from rich.console import Console  # pylint: disable=import-outside-toplevel
        from rich.table import Table  # pylint: disable=import-outside-toplevel
        from rich.bar import Bar  # pylint: disable=import-outside-toplevel

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
                f"{round(total * multiplier, digits):.{digits}f}",
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


def main(arg_list: list[str] | None = None):
    args = parse_args(arg_list)

    run(args.source, args.average, args.seed, args.probabilities, args.digits, args.multiplier)


if __name__ == "__main__":
    main()
