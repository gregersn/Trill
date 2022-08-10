"""Test miscellanous Troll rolls."""
from typing import Any, List

import pytest

from trill.interpreter import Interpreter
from trill.parser import Parser
from trill.tokenizer import Scanner
from trill.ast.printer import ASTPrinter

rolls: List[str] = [
    '6',
    'd6',
    '5d6',
    '(4+1)d6',
    '(d4)d6',
    '11/3',
    '3*d6',
    '-d7',
    'sum 5d6',
    'sgn (d7-3)',
    'sum 3d6+4',
    'z9',
    '3z9',
    'd4#d6',
    '10#(sum 5d6)',
    '3d6 U 3d8',
    '3d6;10d4',
    'd6 U 3d8',
    '3d6 U d8',
    '1..6',
    '{}',
    '{1, 2, 3}',
    'count {}',
    'count {1, 2, 3}',
]

tokenizer_results = [1, 2, 3, 7, 6, 3, 4, 3, 4, 7, 6, 2, 3, 5, 8, 7, 7, 6, 6, 3, 2, 7, 3, 8]

parse_results: List[List[str]] = [
    ['6'],
    ['(d 6)'],
    ['(d 5 6)'],
    ['(d (group (+ 4 1)) 6)'],
    ['(d (group (d 4)) 6)'],
    ['(/ 11 3)'],
    ['(* 3 (d 6))'],
    ['(- (d 7))'],
    ['(sum (d 5 6))'],
    ['(sgn (group (- (d 7) 3)))'],
    ['(+ (sum (d 3 6)) 4)'],
    ['(z 9)'],
    ['(z 3 9)'],
    ['(# (d 4) (d 6))'],
    ['(# 10 (group (sum (d 5 6))))'],
    ['(U (d 3 6) (d 3 8))'],
    ['(d 3 6)', '(d 10 4)'],
    ['(U (d 6) (d 3 8))'],
    ['(U (d 3 6) (d 8))'],
    ['(.. 1 6)'],
    ['(collection )'],
    ['(collection 1 2 3)'],
    ['(count (collection ))'],
    ['(count (collection 1 2 3))'],
]

interpret_results: List[List[Any]] = [
    [6],
    [3.5],
    [[3.5, 3.5, 3.5, 3.5, 3.5]],
    [[3.5, 3.5, 3.5, 3.5, 3.5]],
    [[3.5, 3.5]],
    [11 // 3],
    [3 * 3.5],
    [-4],
    [5 * 3.5],
    [1],
    [3 * 3.5 + 4],
    [4.5],
    [[4.5, 4.5, 4.5]],
    [[3.5, 3.5]],
    [[5 * 3.5] * 10],
    [[3.5, 3.5, 3.5, 4.5, 4.5, 4.5]],
    [[3.5] * 3, [2.5] * 10],
    [[3.5, 4.5, 4.5, 4.5]],
    [[3.5, 3.5, 3.5, 4.5]],
    [[1, 2, 3, 4, 5, 6]],
    [[]],
    [[1, 2, 3]],
    [0],
    [3],
]


@pytest.mark.parametrize("result_list", [tokenizer_results, parse_results, interpret_results])
def test_answers(result_list: List[Any]):
    assert len(result_list) == len(rolls)


@pytest.mark.parametrize("roll,result", zip(rolls, tokenizer_results))
def test_tokenizer(roll: str, result: int):
    scanner = Scanner(roll)
    res = scanner.scan_tokens()
    assert len(res) == result + 1, roll


@pytest.mark.parametrize("roll,result", zip(rolls, parse_results))
def test_parse(roll: str, result: List[str]):
    scanner = Scanner(roll)
    tokens = scanner.scan_tokens()
    parser = Parser(tokens)
    expression = parser.parse()
    res = ASTPrinter().print(expression)
    assert res == result, roll


@pytest.mark.parametrize("roll,result", zip(rolls, interpret_results))
def test_interpret(roll: str, result: List[Any]):
    scanner = Scanner(roll)
    parser = Parser(scanner.scan_tokens())
    expression = parser.parse()
    res = Interpreter().interpret(expression, average=True)
    assert res == result, roll
