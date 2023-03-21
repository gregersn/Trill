"""Test cases."""
from dataclasses import dataclass
from typing import Any, Sequence, Optional


@dataclass
class TestCase:
    roll: str
    token_count: Optional[int]
    parse_result: Optional[Sequence[str]]
    interpret_result: Optional[Sequence[Any]]
    error: Optional[str] = None


testcases: Sequence[TestCase] = [
    TestCase('6', 1, ['6'], [6]),
    TestCase('d6', 2, ['(d 6)'], [3.5]),
    TestCase('5d6', 3, ['(d 5 6)'], [[3.5, 3.5, 3.5, 3.5, 3.5]]),
    TestCase('(4+1)d6', 7, ['(d (group (+ 4 1)) 6)'], [[3.5, 3.5, 3.5, 3.5, 3.5]]),
    TestCase('(d4)d6', 6, ['(d (group (d 4)) 6)'], [[3.5, 3.5]]),
    TestCase('11/3', 3, ['(/ 11 3)'], [11 // 3]),
    TestCase('3*d6', 4, ['(* 3 (d 6))'], [3 * 3.5]),
    TestCase('-d7', 3, ['(- (d 7))'], [-4]),
    TestCase('sum 5', 2, ['(sum 5)'], [5]),
    TestCase('sum d6', 3, ['(sum (d 6))'], [3.5]),
    TestCase('sum 5d6', 4, ['(sum (d 5 6))'], [5 * 3.5]),
    TestCase('sgn (d7-3)', 7, ['(sgn (group (- (d 7) 3)))'], [1]),
    TestCase('sum 3d6+4', 6, ['(+ (sum (d 3 6)) 4)'], [3 * 3.5 + 4]),
    TestCase('z9', 2, ['(z 9)'], [4.5]),
    TestCase('3z9', 3, ['(z 3 9)'], [[4.5, 4.5, 4.5]]),
    TestCase('d4#d6', 5, ['(# (d 4) (d 6))'], [[3.5, 3.5]]),
    TestCase('10#(sum 5d6)', 8, ['(# 10 (group (sum (d 5 6))))'], [[5 * 3.5] * 10]),
    TestCase('3d6 U 3d8', 7, ['(U (d 3 6) (d 3 8))'], [[3.5, 3.5, 3.5, 4.5, 4.5, 4.5]]),
    TestCase('3d6;', 4, None, None, "Parser-error at line 1, column 3: Unexpected semicolon: ;"),
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
    TestCase('largest 3 {4, 5, 2, 4, 7, 2}', 15, None, [[4, 5, 7]]),
    TestCase('largest 3 4d6', 5, ["(largest 3 (d 4 6))"], [[3.5, 3.5, 3.5]]),
    TestCase('largest 1 {1, 2} + 1', 9, ["(+ (largest 1 (collection 1 2)) 1)"], [3]),
    TestCase('least 3 {4, 5, 2, 4, 7, 2}', 15, None, [[2, 2, 4]]),
    TestCase('2 <= {1, 2, 3}', 9, ['(<= 2 (collection 1 2 3))'], [[2, 3]]),
    TestCase('2 < {1, 2, 3}', 9, ['(< 2 (collection 1 2 3))'], [[3]]),
    TestCase('2 >= {1, 2, 3}', 9, ['(>= 2 (collection 1 2 3))'], [[1, 2]]),
    TestCase('2 > {1, 2, 3}', 9, ['(> 2 (collection 1 2 3))'], [[1]]),
    TestCase('2 = {1, 2, 3}', 9, ['(= 2 (collection 1 2 3))'], [[2]]),
    TestCase('2 =/= {1, 2, 3}', 9, ['(=/= 2 (collection 1 2 3))'], [[1, 3]]),
    TestCase('3 <= d6', 4, ['(<= 3 (d 6))'], [[3.5]]),
    TestCase('3 <= 5 >= d6', 6, ['(<= 3 (>= 5 (d 6)))'], [[3.5]]),
    TestCase('3 <= 5 >= d4', 6, ['(<= 3 (>= 5 (d 4)))'], [[]]),
    TestCase('{1, 2, 3, 4} drop 3', 11, ['(drop (collection 1 2 3 4) 3)'], [[1, 2, 4]]),
    TestCase('d6 drop d6', 5, ['(drop (d 6) (d 6))'], [[]]),
    TestCase('{1, 2, 3, 4} keep 3', 11, ['(keep (collection 1 2 3 4) 3)'], [[3]]),
    TestCase('{2, 2, 3} drop {2, 4}', None, None, [[3]]),
    TestCase('d6 keep d6', 5, ['(keep (d 6) (d 6))'], [[3.5]]),
    TestCase('{2, 2, 3} -- {2, 4}', 13, ['(-- (collection 2 2 3) (collection 2 4))'], [[2, 3]]),
    TestCase('different {2, 1, 2}', 8, ['(different (collection 2 1 2))'], [[1, 2]]),
    TestCase('median {2, 6, 23}', 8, ['(median (collection 2 6 23))'], [6]),
    TestCase('x := d6; x*x', 8, ['(block (assign x (d 6)); (* x x))'], [3.5 * 3.5]),
    TestCase(
        'x := d6; y := d8; x*x*y*y',
        17,
        ['(block (assign x (d 6)); (assign y (d 8)); (* (* (* x x) y) y))'],
        [3.5 * 3.5 * 4.5 * 4.5],
    ),
    TestCase(
        'x := 2; (x := 1; x) U x',
        13,
        ['(block (assign x 2); (U (block (assign x 1); x) x))'],
        [[1, 2]],
    ),
    TestCase('x := 3d6; x', 7, ['(block (assign x (d 3 6)); x)'], [[3.5, 3.5, 3.5]]),
    TestCase(
        'x := 1; y := 3; if x = y then 2*x else max (x U y)',
        23,
        ['(block (assign x 1); (assign y 3); (if (= x y) (* 2 x) (max (group (U x y)))))'],
        [3],
    ),
    TestCase(
        'x := 2; y := 2; if x = y then 2*x else max (x U y)',
        23,
        ['(block (assign x 2); (assign y 2); (if (= x y) (* 2 x) (max (group (U x y)))))'],
        [4],
    ),
    TestCase('?0.9', 2, ['(? 0.9)'], [1]),
    TestCase('?0.1', 2, ['(? 0.1)'], [[]]),
    TestCase(
        'x := 2; y := 3; if x = 2 & y = 3 then 42 else 24',
        20,
        ['(block (assign x 2); (assign y 3); (if (& (= x 2) (= y 3)) 42 24))'],
        [42],
    ),
    TestCase(
        'x := 3; y := 3; if x = 2 & y = 3 then 42 else 24',
        20,
        ['(block (assign x 3); (assign y 3); (if (& (= x 2) (= y 3)) 42 24))'],
        [24],
    ),
    TestCase('foreach x in 1..3 do x+1', 10, ['(foreach x (.. 1 3) (+ x 1))'], [[2, 3, 4]]),
    TestCase('repeat x:=d8 until x<8', 9, ['(repeat until (assign x (d 8)) (< x 8))'], [4.5]),
    TestCase('repeat x:=d8 while x=8', 9, ['(repeat while (assign x (d 8)) (= x 8))'], [4.5]),
    TestCase(
        'repeat x:=2d6 until (min x)=/=(max x)',
        16,
        ['(repeat until (assign x (d 2 6)) (=/= (group (min x)) (group (max x))))'],
        [[3.5, 3.5]],
    ),
    TestCase(
        'accumulate x:=d10 while x=10',
        9,
        ['(accumulate (assign x (d 10)) (= x 10))'],
        [[5.5]],
    ),
    TestCase(
        'N := 2; count 5< N#(accumulate x:=d10 while x=10)',
        20,
        ['(block (assign N 2); (count (< 5 (# N (group (accumulate (assign x (d 10)) (= x 10)))))))'],
        [2],
    ),
    TestCase('dX := 4; dX', 5, ['(block (assign dX 4); dX)'], [4]),
    TestCase('X := 4; d X', 6, ['(block (assign X 4); (d X))'], [2.5]),
    TestCase('N := 3; N d6', 7, ['(block (assign N 3); (d N 6))'], [[3.5, 3.5, 3.5]]),
    TestCase('N := 4; \\ This is a comment\nN d6', 7, ['(block (assign N 4); (d N 6))'], [[3.5, 3.5, 3.5, 3.5]]),
    TestCase('x := 3; x ~ 4', 7, ['(block (assign x 3); (~ x 4))'], [3]),
    TestCase('x ~ 4', 3, ['(~ x 4)'], [4]),
    TestCase('x := 6d6; [max x, count different x]', 14, ['(block (assign x (d 6 6)); (pair (max x) (count (different x))))'], [(3.5, 1)]),
    TestCase('p := [1, 2]; %1 p', 10, ['(block (assign p (pair 1 2)); (%1 p))'], [1]),
    TestCase('p := [1, 2]; %2 p', 10, ['(block (assign p (pair 1 2)); (%2 p))'], [2]),
    TestCase('x := {}; !x', 7, ['(block (assign x (collection )); (! x))'], [1]),
    TestCase('x := 7; !x', 6, ['(block (assign x 7); (! x))'], [[]]),
    TestCase('(min v)*call mul(largest ((count v)-1) v)', 19,
             ['(* (group (min v)) (call mul (largest (group (- (group (count v)) 1)) v)))'], None),
    TestCase("""function foo(v) = v * v\ncall foo(5)""", None, None, [None, 25]),
    TestCase("""function foo(v) = if v then call foo(v - 1) + v else 0\ncall foo(3)""", None, None, [None, 6]),
    TestCase("""function times(x,y) = x*y""", 11, ['(function times (x,y) (* x y))'], None),
    TestCase(
        """function mul(v) =
if v then (min v)*call mul(largest ((count v)-1) v)
else 1
call mul(5d10)
    """, 37,
        ['(function mul (v) (if v (* (group (min v)) (call mul (largest (group (- (group (count v)) 1)) v))) 1))', '(call mul (d 5 10))'],
        [None, 5.5**5]),
    TestCase("""function even(n) =
if n=0 then 1 else call odd(n-1)
call even(d9)
function odd(n) =
if n=0 then 0 else call even(n-1)""", 46, None, [None, None, 0]),
    TestCase("""function down(n) =
x := d n;
if x=1 then 1 else x + call down(x)
call down(10)""", 30, ['(function down (n) (block (assign x (d n)); (if (= x 1) 1 (+ x (call down x)))))', '(call down 10)'], None),
    TestCase("""sum largest 3 4d6""", 6, ["(sum (largest 3 (d 4 6)))"], [3 * 3.5]),
    TestCase("' sum largest 3 4d6", 7, ["(textbox 1 (sum (largest 3 (d 4 6))))"], [['10.5']]),
    TestCase("6 ' sum largest 3 4d6", 8, ["(textbox 6 (sum (largest 3 (d 4 6))))"], [['10.5', '10.5', '10.5', '10.5', '10.5', '10.5']]),
    TestCase('"1|>two|>three"', 1, ["1|>two|>three"], ["1    \ntwo  \nthree"]),
    TestCase('"1" |> "two" |> "three"', 5, ["(textalign 1 (textalign two three))"], ["1    \ntwo  \nthree"]),
    TestCase('"1" <| "two" <| "three"', 5, ["(textalign 1 (textalign two three))"], ["    1\n  two\nthree"]),
    TestCase('"1" <> "two" <> "three"', 5, ["(textalign 1 (textalign two three))"], ["  1  \n two \nthree"]),
    TestCase('"1" || "two" <> "three"', 5, ["(textalign 1 (textalign two three))"], ["1 two \n three"]),
    TestCase(
        '"Str |>Dex|>Con|>Int|>Wis|>Chr" || 6\'sum largest 3 4d6',
        10,
        ["(textalign Str |>Dex|>Con|>Int|>Wis|>Chr (textbox 6 (sum (largest 3 (d 4 6)))))"],
        ['Str 10.5\nDex 10.5\nCon 10.5\nInt 10.5\nWis 10.5\nChr 10.5'],
    ),
    TestCase('"Foo "|| 3d6', 5, ["(textalign Foo  (d 3 6))"], ['Foo 3.5\n    3.5\n    3.5']),
    TestCase('largest(1,3d20)', 8, None, None, "Parser-error at line 1, column 9: Expected a semi colon"),
    TestCase('largest 1 2d20 + 7 + d4', 10, ["(+ (+ (largest 1 (d 2 20)) 7) (d 4))"], [10.5 + 7 + 2.5]),
    TestCase("""function add(a, b) =
        a + b
        call add(1, 2)""", 18, ["(function add (a,b) (+ a b))", "(call add 1 2)"], [None, 3]),
    TestCase("""compositional product(1,id,times)
        function id(x) = x
        function times(x,y) = x*y
        call product({1, 2, 4})""", 38, ["(compositional product 1 id times)", "(function id (x) x)", "(function times (x,y) (* x y))", "(call product (collection 1 2 4))"],
             [None, None, None, 8]),
    TestCase("""compositional product(1,sum,*)
                call product({})
                call product(3)
                call product({1, 2, 4})""", 31, ["(compositional product 1 sum *)", "(call product (collection ))", "(call product 3)", "(call product (collection 1 2 4))"], [None, 1, 3, 8])
]
