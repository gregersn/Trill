"""Troll interpreter."""
from typing import ChainMap, Dict, Iterable, TypeVar, List, Any, Union, cast
import random
from .ast import expression
from .ast import statement
from .tokens import TokenType

T = TypeVar('T')


class Interpreter(expression.ExpressionVisitor[T], statement.StatementVisitor[T]):
    average: bool = False

    # variables: Dict[str, Union[int, str]] = {}
    variables: ChainMap[str, Union[int, str]] = ChainMap({})
    functions: Dict[str, statement.Function] = {}

    def __repr__(self):
        return "<Interpreter >"

    def push(self):
        self.variables = self.variables.new_child()

    def pop(self):
        self.variables = self.variables.parents

    def interpret(self, statements: List[Union[expression.Expression, statement.Statement]], average: bool = False):
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

    def visit_Literal_Expression(self, expr: expression.Literal) -> Union[str, int, float]:
        return expr.value

    def evaluate(self, expr: expression.Expression):
        return expr.accept(self)

    def visit_Unary_Expression(self, expr: expression.Unary):
        right = self.evaluate(expr.right)

        if expr.operator.token_type == TokenType.NOT:
            if not right:
                return 1
            return []

        if expr.operator.token_type == TokenType.PAIR_VALUE:
            v = expr.operator.literal
            return right[v - 1]

        if expr.operator.token_type == TokenType.MINUS:
            return -right

        if expr.operator.token_type == TokenType.DICE:
            start = 0 if expr.operator.lexeme == 'z' else 1
            if self.average:
                return (right + start) / 2
            else:
                return random.randint(start, right)

        if expr.operator.token_type == TokenType.SUM:
            return sum(right)

        if expr.operator.token_type == TokenType.SIGN:
            if right == 0:
                return 0
            return right / abs(right)

        if expr.operator.token_type == TokenType.CHOOSE:
            if self.average:
                return right[len(right) // 2]

            return random.choice(right)

        if expr.operator.token_type == TokenType.MIN:
            return min(right)

        if expr.operator.token_type == TokenType.MAX:
            return max(right)

        if expr.operator.token_type == TokenType.COUNT:
            return len(right)

        if expr.operator.token_type == TokenType.MINIMAL:
            min_value = min(right)
            return [
                min_value,
            ] * right.count(min_value)

        if expr.operator.token_type == TokenType.MAXIMAL:
            max_value = max(right)
            return [
                max_value,
            ] * right.count(max_value)

        if expr.operator.token_type == TokenType.MEDIAN:
            mid_point = len(right) // 2
            return list(sorted(right))[mid_point]

        if expr.operator.token_type == TokenType.DIFFERENT:
            return list(set(right))

        if expr.operator.token_type == TokenType.PROBABILITY:
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

        raise Exception(f"Unknown operator {expr.operator.token_type} in unary expression")

    def visit_Binary_Expression(self, expr: expression.Binary):
        if expr.operator.token_type == TokenType.DEFAULT:
            left = self.evaluate(expr.left)
            return left or self.evaluate(expr.right)

        if expr.operator.token_type == TokenType.SAMPLES:
            output: List[Union[int, float, str]] = []
            for _ in range(int(self.evaluate(expr.left))):
                new_val = self.evaluate(expr.right)
                if isinstance(new_val, Iterable):
                    output = output + list(new_val)
                else:
                    output.append(new_val)
            return output

        if expr.operator.token_type == TokenType.LARGEST:
            count = self.evaluate(expr.left)
            if count == 0:
                return []
            return list(sorted(self.evaluate(expr.right)))[-count:]

        if expr.operator.token_type == TokenType.LEAST:
            count = self.evaluate(expr.left)
            if count == 0:
                return []
            return list(sorted(self.evaluate(expr.right)))[:-count]

        if isinstance(expr.left, expression.Literal):
            val = self.evaluate(expr.left)
            if isinstance(val, str):
                left = self.variables.get(val)
            else:
                left = val
        else:
            left = self.evaluate(expr.left)

        if isinstance(expr.right, expression.Literal):
            val = self.evaluate(expr.right)
            if isinstance(val, str):
                right = self.variables.get(val)
            else:
                right = val
        else:
            right = self.evaluate(expr.right)

        if not (isinstance(left, (float, int, list)) and isinstance(right, (float, int, list))):
            raise Exception("Whatt now")

        if expr.operator.token_type == TokenType.DICE:
            start = 0 if expr.operator.lexeme == 'z' else 1
            if self.average:
                return [
                    (right + start) / 2,
                ] * int(left)
            else:
                return [random.randint(start, right) for _ in range(left)]

        if expr.operator.token_type == TokenType.RANGE:
            return list(range(left, right + 1))

        if expr.operator.token_type == TokenType.UNION:
            if isinstance(left, (int, float)):
                left = [left]

            if isinstance(right, (int, float)):
                right = [right]

            return left + right

        if expr.operator.token_type == TokenType.PICK:
            if isinstance(left, int):
                raise Exception("Unexpected integer.")
            samples = min(len(left), right)
            if self.average:
                offset = samples // 2
                mid_point = len(left) // 2
                return left[mid_point - offset:mid_point + offset + 1]

            return random.sample(left, samples)

        if expr.operator.token_type == TokenType.DROP:
            if isinstance(left, (int, float)):
                left = [left]

            if isinstance(right, (int, float)):
                right = [right]
            return [x for x in left if x not in right]

        if expr.operator.token_type == TokenType.KEEP:
            if isinstance(left, (int, float)):
                left = [left]

            if isinstance(right, (int, float)):
                right = [right]
            return [x for x in left if x in right]

        if expr.operator.token_type == TokenType.MINUSMINUS:
            if isinstance(left, (int, float)):
                left = [left]

            if isinstance(right, (int, float)):
                right = [right]

            output = list(left)
            for v in right:
                if v in output:
                    output.remove(v)

            return output

        if expr.operator.token_type == TokenType.PLUS:
            return left + right

        if expr.operator.token_type == TokenType.MINUS:
            return left - right

        if expr.operator.token_type == TokenType.DIVIDE:
            return left // right

        if expr.operator.token_type == TokenType.MULTIPLY:
            return left * right

        if expr.operator.token_type == TokenType.AND:
            return left and right

        if expr.operator.token_type in [
                TokenType.LESS_THAN,
                TokenType.LESS_THAN_OR_EQUAL,
                TokenType.GREATER_THAN,
                TokenType.GREATER_THAN_OR_EQUAL,
                TokenType.EQUAL,
                TokenType.NOT_EQUAL,
        ]:
            if isinstance(right, (int, float)):
                right = [right]

            if expr.operator.token_type == TokenType.LESS_THAN_OR_EQUAL:
                return [v for v in right if left <= v]

            if expr.operator.token_type == TokenType.LESS_THAN:
                return [v for v in right if left < v]

            if expr.operator.token_type == TokenType.GREATER_THAN_OR_EQUAL:
                return [v for v in right if left >= v]

            if expr.operator.token_type == TokenType.GREATER_THAN:
                return [v for v in right if left > v]

            if expr.operator.token_type == TokenType.EQUAL:
                return [v for v in right if left == v]

            if expr.operator.token_type == TokenType.NOT_EQUAL:
                return [v for v in right if left != v]

        raise Exception(f"Unknown operator {expr.operator.token_type} in binary expression")

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
        self.variables[expr.name.literal] = self.evaluate(expr.value)
        # return self.variables[expr.name.literal]

    def visit_Variable_Expression(self, expr: expression.Variable):
        return self.variables.get(expr.name.literal, None)

    def visit_Conditional_Expression(self, stmt: expression.Conditional):
        if self.evaluate(stmt.condition):
            return self.evaluate(stmt.truth)
        return self.evaluate(stmt.falsy)

    def visit_Foreach_Expression(self, expr: expression.Foreach):
        output: List[Any] = []
        self.push()
        for val in self.evaluate(expr.source):
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

        res = self.variables.get(action_variable_name.literal)
        self.pop()
        return res

    def visit_Accumulate_Expression(self, stmt: expression.Accumulate) -> List[Union[int, float, str, None]]:
        action = stmt.action
        qualifier = stmt.qualifier

        result: List[Union[int, float, str, None]] = []
        self.push()
        action_variable_name = action.name
        self.evaluate(action)
        result.append(self.variables.get(action_variable_name.literal))

        while self.evaluate(qualifier):
            self.evaluate(action)
            val = self.variables.get(action_variable_name.literal)
            if isinstance(val, (int, float)):
                result.append(val)
            elif isinstance(val, list):
                result += val
            else:
                raise Exception("Unknown stuff")

        self.pop()

        return result

    def visit_Function_Statement(self, stmt: statement.Function):
        self.functions[stmt.name.literal] = stmt

    def visit_Call_Expression(self, expr: expression.Call):
        assert expr.name.literal in self.functions
        stmt = self.functions[expr.name.literal]
        self.push()
        for name, value in zip(stmt.parameters, expr.parameters):
            self.variables[name.literal] = self.evaluate(value)
        res = self.execute(stmt.expression)
        self.pop()
        return res

    def visit_Print_Statement(self, stmt: statement.Print):
        repeats = stmt.repeats
        expr = stmt.expression

        return [str(self.evaluate(expr)) for _ in range(repeats)]
