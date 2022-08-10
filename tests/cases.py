"""Test cases."""
from dataclasses import dataclass
from typing import Any, List, Optional


@dataclass
class TestCase:
    roll: str
    token_count: Optional[int]
    parse_result: Optional[List[str]]
    interpret_result: Optional[List[Any]]


testcases: List[TestCase] = [
    TestCase('6', 1, ['6'], [6]),
    TestCase('d6', 2, ['(d 6)'], [3.5]),
    TestCase('5d6', 3, ['(d 5 6)'], [[3.5, 3.5, 3.5, 3.5, 3.5]]),
    TestCase('(4+1)d6', 7, ['(d (group (+ 4 1)) 6)'], [[3.5, 3.5, 3.5, 3.5, 3.5]]),
    TestCase('(d4)d6', 6, ['(d (group (d 4)) 6)'], [[3.5, 3.5]]),
    TestCase('11/3', 3, ['(/ 11 3)'], [11 // 3]),
    TestCase('3*d6', 4, ['(* 3 (d 6))'], [3 * 3.5]),
    TestCase('-d7', 3, ['(- (d 7))'], [-4]),
    TestCase('sum 5d6', 4, ['(sum (d 5 6))'], [5 * 3.5]),
    TestCase('sgn (d7-3)', 7, ['(sgn (group (- (d 7) 3)))'], [1]),
    TestCase('sum 3d6+4', 6, ['(+ (sum (d 3 6)) 4)'], [3 * 3.5 + 4]),
    TestCase('z9', 2, ['(z 9)'], [4.5]),
    TestCase('3z9', 3, ['(z 3 9)'], [[4.5, 4.5, 4.5]]),
    TestCase('d4#d6', 5, ['(# (d 4) (d 6))'], [[3.5, 3.5]]),
    TestCase('10#(sum 5d6)', 8, ['(# 10 (group (sum (d 5 6))))'], [[5 * 3.5] * 10]),
    TestCase('3d6 U 3d8', 7, ['(U (d 3 6) (d 3 8))'], [[3.5, 3.5, 3.5, 4.5, 4.5, 4.5]]),
    TestCase('3d6;10d4', 7, ['(d 3 6)', '(d 10 4)'], [[3.5] * 3, [2.5] * 10]),
    TestCase('d6 U 3d8', 6, ['(U (d 6) (d 3 8))'], [[3.5, 4.5, 4.5, 4.5]]),
    TestCase('3d6 U d8', 6, ['(U (d 3 6) (d 8))'], [[3.5, 3.5, 3.5, 4.5]]),
    TestCase('1..6', 3, ['(.. 1 6)'], [[1, 2, 3, 4, 5, 6]]),
    TestCase('{}', 2, ['(collection )'], [[]]),
    TestCase('{1, 2, 3}', 7, ['(collection 1 2 3)'], [[1, 2, 3]]),
    TestCase('count {}', 3, ['(count (collection ))'], [0]),
    TestCase('count {1, 2, 3}', 8, ['(count (collection 1 2 3))'], [3]),
    TestCase('{d6, 3d8}', 8, ['(collection (d 6) (d 3 8))'], [[3.5, 4.5, 4.5, 4.5]]),
    TestCase('{1..6}', 5, ['(collection (.. 1 6))'], [[1, 2, 3, 4, 5, 6]]),
    TestCase('choose {-1, 0, 1}', 9, ['(choose (collection (- 1) 0 1))'], [0]),
    TestCase('{1..10} pick 3', 7, ['(pick (collection (.. 1 10)) 3)'], [[5, 6, 7]]),
    TestCase('{1, 2, 3} pick 4', 9, ['(pick (collection 1 2 3) 4)'], [[1, 2, 3]]),
    TestCase('min {1, 2, 3}', 8, ['(min (collection 1 2 3))'], [1]),
    TestCase('max {1, 2, 3}', 8, ['(max (collection 1 2 3))'], [3]),
    TestCase('minimal {1, 1, 2, 3, 3}', 12, ['(minimal (collection 1 1 2 3 3))'], [[1, 1]]),
    TestCase('maximal {1, 1, 2, 3, 3}', 12, ['(maximal (collection 1 1 2 3 3))'], [[3, 3]]),
]
