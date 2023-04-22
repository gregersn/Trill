"""Trill - Troll interpreter."""
from typing import Optional
from .tokenizer import Tokenizer
from .parser import Parser
from .interpreter import Interpreter
from .error import handler as error_handler


def trill(roll: str, seed: Optional[int] = None):
    tokens = Tokenizer(roll).scan_tokens()

    if error_handler.had_error:
        return [None, error_handler.error_report]

    parsed = Parser(tokens).parse()

    if error_handler.had_error:
        return [None, error_handler.error_report]

    result = Interpreter(seed).interpret(parsed)

    return [result, error_handler.error_report]
