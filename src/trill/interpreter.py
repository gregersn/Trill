"""Troll interpreter."""
from typing import ChainMap, Dict, Iterable, Sequence, TypeVar, List, Any, Union, cast
import random
from trill.string import process_string

from trill.types import Number, NumberList
from .ast import expression
from .ast import statement
from .tokens import Token, TokenType

T = TypeVar('T')


class UnknownOperator(Exception):
    """Unknown operator."""


class UnknownType(Exception):
    """Unknown data types in input."""


class Interpreter(expression.ExpressionVisitor[T], statement.StatementVisitor[T]):
    average: bool = False

    # variables: Dict[str, Union[int, str]] = {}
    variables: ChainMap[str, Union[Number, NumberList, str]] = ChainMap({})
    functions: Dict[str, Union[statement.Function, statement.Compositional]] = {}

    def __repr__(self):
        return "<Interpreter >"

    def push(self):
        self.variables = self.variables.new_child()

    def pop(self):
        self.variables = self.variables.parents

    def interpret(self,
                  statements: List[Union[expression.Expression, statement.Statement]],
                  average: bool = False) -> List[Union[Number, NumberList, str]]:
        self.average = average
        self.variables = ChainMap({})
        output: List[Any] = []

        # Find all function delcarations first, so that they are available on run.
        for stmt in statements:
            if isinstance(stmt, statement.Function):
                output.append(self.execute(stmt))

        # Run statements, skip function declarations, as they are already done.
        for stmt in statements:
            if isinstance(stmt, statement.Function):
                continue
            if isinstance(stmt, statement.Statement):
                output.append(self.execute(stmt))
            if isinstance(stmt, expression.Expression):
                output.append(self.evaluate(stmt))
        return output

    def execute(self, stmt: statement.Statement):
        return stmt.accept(self)

    def visit_Literal_Expression(self, expr: expression.Literal) -> Union[str, int, float, List[str], List[List[str]], None]:
        if isinstance(expr.value, str):
            return process_string(expr.value)
        return expr.value

    def evaluate(self, expr: expression.Expression) -> Union[Number, NumberList]:
        return expr.accept(self)

    def visit_Unary_Expression(self, expr: expression.Unary):
        token_type = expr.operator.token_type

        right = self.evaluate(expr.right)

        if token_type == TokenType.NOT:
            if not right:
                return 1
            return cast(Sequence[int], [])

        if token_type == TokenType.PAIR_VALUE:
            v = expr.operator.literal
            assert isinstance(v, int)
            assert isinstance(right, (list, tuple)), type(right)
            return right[v - 1]

        if token_type == TokenType.MINUS:
            assert isinstance(right, (int, float))
            return -right

        if token_type == TokenType.DICE:
            start = 0 if expr.operator.lexeme == 'z' else 1
            assert isinstance(right, int)
            if self.average:
                return (right + start) / 2

            return random.randint(start, right)

        if token_type == TokenType.SUM:
            if isinstance(right, (int, float)):
                right = [right]
            return sum(right)

        if token_type == TokenType.SIGN:
            if right == 0:
                return 0
            assert isinstance(right, (int, float))
            return right / abs(right)

        if token_type == TokenType.CHOOSE:
            assert isinstance(right, list)
            if self.average:
                return right[len(right) // 2]

            return random.choice(right)

        if token_type == TokenType.MIN:
            assert isinstance(right, list)
            return min(right)

        if token_type == TokenType.MAX:
            assert isinstance(right, list)
            return max(right)

        if token_type == TokenType.COUNT:
            assert isinstance(right, list)
            return len(right)

        if token_type == TokenType.MINIMAL:
            assert isinstance(right, list)
            min_value = min(right)
            return [
                min_value,
            ] * right.count(min_value)

        if token_type == TokenType.MAXIMAL:
            assert isinstance(right, list)
            max_value = max(right)
            return [
                max_value,
            ] * right.count(max_value)

        if token_type == TokenType.MEDIAN:
            assert isinstance(right, list)
            mid_point = len(right) // 2
            return list(sorted(right))[mid_point]

        if token_type == TokenType.DIFFERENT:
            assert isinstance(right, list)
            return list(set(right))

        if token_type == TokenType.PROBABILITY:
            assert isinstance(right, float)
            if self.average:
                if right < 0.5:
                    val = 1.0
                else:
                    val = 0.0
            else:
                val = random.random()

            if val < right:
                return 1
            else:
                return cast(List[Any], [])

        raise UnknownOperator(
            f"Unknown operator {token_type} in unary expression")

    def visit_Binary_Expression(self, expr: expression.Binary):
        token_type = expr.operator.token_type

        if token_type == TokenType.DEFAULT:
            left = self.evaluate(expr.left)
            return left or self.evaluate(expr.right)

        left_value = self.evaluate(expr.left)
        right_value = self.evaluate(expr.right)

        if token_type == TokenType.SAMPLES:
            output: List[Union[int, float, str]] = []
            assert isinstance(left_value, (int, float))
            for _ in range(int(left_value)):
                new_val = right_value
                if isinstance(new_val, Iterable):
                    output = output + list(new_val)
                else:
                    output.append(new_val)
            return output

        if token_type == TokenType.LARGEST:
            count = left_value
            if count == 0:
                return cast(Sequence[int], [])
            assert isinstance(right_value, list)
            assert isinstance(count, int)
            return list(sorted(right_value))[-count:]

        if token_type == TokenType.LEAST:
            count = left_value
            if count == 0:
                return cast(Sequence[int], [])
            assert isinstance(right_value, list)
            assert isinstance(count, int)
            return list(sorted(right_value))[:-count]

        if isinstance(expr.left, expression.Literal):
            val = left_value
            if isinstance(val, str):
                left = self.variables.get(val)
            else:
                left = val
        else:
            left = left_value

        if isinstance(expr.right, expression.Literal):
            val = right_value
            if isinstance(val, str):
                right = self.variables.get(val)
            else:
                right = val
        else:
            right = right_value

        if not (isinstance(left, (float, int, list)) and isinstance(right, (float, int, list))):
            raise UnknownType("Whatt now")

        if token_type == TokenType.DICE:
            start = 0 if expr.operator.lexeme == 'z' else 1
            assert isinstance(right, (int))
            assert isinstance(left, (float, int))
            if self.average:
                return [(right + start) / 2] * int(left)

            return [random.randint(start, right) for _ in range(int(left))]

        if token_type == TokenType.RANGE:
            assert isinstance(right, (int))
            assert isinstance(left, (int))
            return list(range(left, right + 1))

        if token_type == TokenType.UNION:
            if isinstance(left, (int, float)):
                left = [left]

            if isinstance(right, (int, float)):
                right = [right]

            return left + right

        if token_type == TokenType.PICK:
            if isinstance(left, (int, float)):
                raise UnknownType("Unexpected scalar.")

            assert isinstance(right, (int))
            samples = min(len(left), right)
            if self.average:
                offset = samples // 2
                mid_point = len(left) // 2
                return left[mid_point - offset:mid_point + offset + 1]

            return random.sample(left, samples)

        if token_type == TokenType.DROP:
            if isinstance(left, (int, float)):
                left = [left]

            if isinstance(right, (int, float)):
                right = [right]
            return [x for x in left if x not in right]

        if token_type == TokenType.KEEP:
            if isinstance(left, (int, float)):
                left = [left]

            if isinstance(right, (int, float)):
                right = [right]
            return [x for x in left if x in right]

        if token_type == TokenType.MINUSMINUS:
            if isinstance(left, (int, float)):
                left = [left]

            if isinstance(right, (int, float)):
                right = [right]

            output = list(left)
            for v in right:
                if v in output:
                    output.remove(v)

            return output

        if token_type == TokenType.AND:
            return left and right

        if token_type in [
                TokenType.LESS_THAN,
                TokenType.LESS_THAN_OR_EQUAL,
                TokenType.GREATER_THAN,
                TokenType.GREATER_THAN_OR_EQUAL,
                TokenType.EQUAL,
                TokenType.NOT_EQUAL,
        ]:
            if isinstance(right, (int, float)):
                right = [right]

            assert isinstance(left, (int, float))

            if token_type == TokenType.LESS_THAN_OR_EQUAL:
                return [v for v in right if left <= v]

            if token_type == TokenType.LESS_THAN:
                return [v for v in right if left < v]

            if token_type == TokenType.GREATER_THAN_OR_EQUAL:
                return [v for v in right if left >= v]

            if token_type == TokenType.GREATER_THAN:
                return [v for v in right if left > v]

            if token_type == TokenType.EQUAL:
                return [v for v in right if left == v]

            if token_type == TokenType.NOT_EQUAL:
                return [v for v in right if left != v]

        if isinstance(left, list):
            assert len(left) == 1
            left = left[0]

        if isinstance(right, list):
            assert len(right) == 1
            right = right[0]

        assert isinstance(left, (int, float))
        assert isinstance(right, (int, float))

        if token_type == TokenType.PLUS:
            return left + right

        if token_type == TokenType.MINUS:
            return left - right

        if token_type == TokenType.DIVIDE:
            return left // right

        if token_type == TokenType.MULTIPLY:
            return left * right

        raise UnknownOperator(
            f"Unknown operator {expr.operator.token_type} in binary expression")

    def visit_Grouping_Expression(self, expr: expression.Grouping):
        return self.evaluate(expr.expression)

    def visit_Block_Expression(self, expr: expression.Block):
        val = None
        self.push()
        for stmt in expr.statements:
            val = self.evaluate(stmt)
        self.pop()
        return val

    def visit_Pair_Expression(self, expr: expression.Pair):
        return (self.evaluate(expr.first), self.evaluate(expr.second))

    def visit_List_Expression(self, expr: expression.List):
        output: List[Any] = []
        for value in expr.value:
            res = self.evaluate(value)
            if isinstance(res, list):
                output += res
            else:
                output.append(res)

        return output

    def visit_Assign_Expression(self, expr: expression.Assign):
        assert isinstance(expr.name.literal, str)
        value = self.evaluate(expr.value)
        self.variables[expr.name.literal] = value
        # return self.variables[expr.name.literal]

    def visit_Variable_Expression(self, expr: expression.Variable):
        assert isinstance(expr.name.literal, str)
        return self.variables.get(expr.name.literal, None)

    def visit_Conditional_Expression(self, stmt: expression.Conditional):
        if self.evaluate(stmt.condition):
            return self.evaluate(stmt.truth)
        return self.evaluate(stmt.falsy)

    def visit_Foreach_Expression(self, expr: expression.Foreach):
        output: List[Any] = []
        self.push()

        values = self.evaluate(expr.source)
        assert isinstance(values, list)
        assert isinstance(expr.iterator.name.literal, str)
        for val in values:
            self.variables[expr.iterator.name.literal] = val
            output.append(self.evaluate(expr.block))
        self.pop()
        return output

    def visit_Repeat_Expression(self, stmt: expression.Repeat):
        condition = stmt.condition
        action = stmt.action
        qualifier = stmt.qualifier

        self.push()
        action_variable_name = action.name
        if condition.token_type == TokenType.WHILE:
            res = self.evaluate(action)
            while self.evaluate(qualifier) and not self.average:
                res = self.evaluate(action)

        if condition.token_type == TokenType.UNTIL:
            res = self.evaluate(action)
            while not self.evaluate(qualifier) and not self.average:
                res = self.evaluate(action)

        assert isinstance(action_variable_name.literal, str)
        res = self.variables.get(action_variable_name.literal)
        self.pop()
        return res

    def visit_Accumulate_Expression(self, stmt: expression.Accumulate) -> List[Union[str, Number, NumberList, None]]:
        action = stmt.action
        qualifier = stmt.qualifier

        result: List[Union[str, Number, NumberList, None]] = []
        self.push()
        action_variable_name = action.name
        self.evaluate(action)
        assert isinstance(action_variable_name.literal, str)
        result.append(self.variables.get(action_variable_name.literal))

        while self.evaluate(qualifier):
            self.evaluate(action)
            val = self.variables.get(action_variable_name.literal)
            if isinstance(val, (int, float)):
                result.append(val)
            elif isinstance(val, list):
                result += val
            else:
                raise UnknownType(f"Unknown type: {type(val)}")

        self.pop()

        return result

    def visit_Function_Statement(self, stmt: statement.Function):
        assert isinstance(stmt.name.literal, str)
        self.functions[stmt.name.literal] = stmt

    def visit_Compositional_Statement(self, stmt: statement.Compositional):
        assert isinstance(stmt.name.literal, str)
        self.functions[stmt.name.literal] = stmt

    def visit_Call_Expression(self, expr: expression.Call):
        assert expr.name.literal in self.functions
        stmt = self.functions[expr.name.literal]

        if isinstance(stmt, statement.Compositional):
            return self.call_compositional(expr, stmt)

        return self.call_function(expr, stmt)

    def call_compositional(self, expr: expression.Call, stmt: statement.Compositional):
        self.push()

        res = stmt.empty.value

        parameter = expr.parameters[0]

        if isinstance(parameter, expression.List):
            operator = stmt.union
            for next_val in parameter.value:
                if isinstance(operator, Token) and operator.token_type == TokenType.IDENTIFIER:
                    res = self.visit_Call_Expression(expression.Call(name=operator, parameters=[expression.Literal(res), next_val]))
                else:
                    res = self.visit_Binary_Expression(expression.Binary(expression.Literal(res), operator=operator, right=next_val))
        else:
            operator = stmt.singleton
            if isinstance(operator, Token) and operator.token_type == TokenType.IDENTIFIER:
                res = self.visit_Call_Expression(expression.Call(name=operator, parameters=[expression.Literal(res)]))
            else:
                res = self.visit_Unary_Expression(expression.Unary(operator=operator, right=parameter))

        self.pop()
        return res

    def call_function(self, expr: expression.Call, stmt: statement.Function):
        self.push()
        for name, value in zip(stmt.parameters, expr.parameters):
            assert isinstance(name.literal, str)
            self.variables[name.literal] = self.evaluate(value)

        assert isinstance(
            stmt.expression, (statement.Expression, statement.Statement))

        if isinstance(stmt.expression, statement.Expression):
            res = self.evaluate(stmt.expression)
            self.pop()
            return res

        res = self.execute(stmt.expression)
        self.pop()
        return res

    def visit_Print_Statement(self, stmt: statement.Print):
        repeats = stmt.repeats
        expr = stmt.expression

        return [str(self.evaluate(expr)) for _ in range(repeats)]

    def visit_TextAlign_Expression(self, expr: expression.TextAlign):
        operator = expr.operator
        left = self.evaluate(expr.left)
        right = self.evaluate(expr.right)

        if isinstance(left, str):
            left = left.split('\n')

        if isinstance(right, str):
            right = right.split('\n')

        if not isinstance(left, list):
            left = [left]
        if not isinstance(right, list):
            right = [right]

        assert isinstance(left, list), f"{left}, {type(left)}"
        assert isinstance(right, list), f"{right}, {type(right)}"

        max_length_left = len(str(max(left, key=lambda x: len(str(x)))))
        max_length_right = len(str(max(right, key=lambda x: len(str(x)))))
        max_length = max(max_length_left, max_length_right)

        if operator.lexeme == '|>':
            output = [f'{t:<{max_length}}' for t in left] + [f'{t:<{max_length}}' for t in right]
            return "\n".join(output)

        if operator.lexeme == '<|':
            output = [f'{t:>{max_length}}' for t in left] + [f'{t:>{max_length}}' for t in right]
            return "\n".join(output)

        if operator.lexeme == '<>':
            output = [f'{t:^{max_length}}' for t in left] + [f'{t:^{max_length}}' for t in right]
            return "\n".join(output)

        if operator.lexeme == '||':
            max_height = max(len(left), len(right))

            left += [' ' * max_length_left] * (max_height - len(left))
            right += [' ' * max_length_right] * (max_height - len(right))

            assert len(left) == len(right)

            preliminary = list(zip(left, right))

            return "\n".join(["".join([str(v) for v in t]) for t in preliminary])
