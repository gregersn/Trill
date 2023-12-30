"""Troll interpreter."""
from typing import ChainMap, Dict, TypeVar, List, Any, Union
import random
from trill import functions
from trill.string import process_string

from trill.types import Number, NumberList
from .ast import expression
from .ast import statement
from .tokens import Token, TokenType

T = TypeVar("T")


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

    def interpret(
        self,
        statements: List[Union[expression.Expression, statement.Statement]],
        average: bool = False,
    ) -> List[Union[Number, NumberList, str]]:
        self.average = average
        self.variables = ChainMap({})
        output: List[Any] = []

        # Find all function delcarations first, so that they are available on run.
        for stmt in statements:
            if isinstance(stmt, statement.Function):
                output.append(stmt.accept(self))

        # Run statements, skip function declarations, as they are already done.
        for stmt in statements:
            if isinstance(stmt, statement.Function):
                continue
            output.append(stmt.accept(self))
        return output

    def visit_Literal_Expression(self, expr: expression.Literal) -> Union[str, int, float, List[str], List[List[str]], None]:
        if isinstance(expr.value, str):
            return process_string(expr.value)
        return expr.value

    def visit_Unary_Expression(self, expr: expression.Unary):
        token_type = expr.operator.token_type
        right = expr.right.accept(self)

        return functions.unary_expression(
            token_type,
            right,
            expr.operator,
            self.average,
        )

    def visit_Binary_Expression(self, expr: expression.Binary):
        token_type = expr.operator.token_type

        left_value = expr.left.accept(self)

        if token_type == TokenType.DEFAULT:
            # If a value (left) is not defined, use the default (right)
            return left_value or expr.right.accept(self)

        right_value = expr.right.accept(self)

        if token_type in functions.COLLECTION_TOKENS:
            return functions.collection_operation(token_type, left_value, right_value)

        left = self.variables.get(left_value, left_value) if isinstance(left_value, str) else left_value
        right = self.variables.get(right_value) if isinstance(right_value, str) else right_value

        if token_type == TokenType.AND:
            return left and right

        if token_type == TokenType.DICE:
            start = 0 if expr.operator.lexeme == "z" else 1
            if not (isinstance(right, int) and isinstance(left, (int, float))):
                raise TypeError(f"Dice average only support ints, got {right} and {left}")

            if self.average:
                return functions.dice_average(right, int(left), start)

            return functions.dice_roll(right, int(left), start)

        if token_type == TokenType.RANGE:
            if not (isinstance(right, int) and isinstance(left, (int,))):
                raise TypeError(f"Range only support ints, got {right} and {left}")
            return list(range(left, right + 1))

        if token_type == TokenType.UNION:
            if not isinstance(left, list):
                left = [left]

            if not isinstance(right, list):
                right = [right]

            return left + right

        if token_type == TokenType.PICK:
            if isinstance(left, (int, float)):
                raise UnknownType("Unexpected scalar.")

            if not isinstance(right, int):
                raise TypeError("Length should be int")

            samples = min(len(left), right)
            if self.average:
                offset = samples // 2
                mid_point = len(left) // 2
                return left[mid_point - offset : mid_point + offset + 1]

            return random.sample(left, samples)

        if token_type in [TokenType.DROP, TokenType.KEEP, TokenType.MINUSMINUS]:
            if not isinstance(left, list):
                left = [left]

            if not isinstance(right, list):
                right = [right]

            if token_type == TokenType.DROP:
                output = [x for x in left if x not in right]

            elif token_type == TokenType.KEEP:
                output = [x for x in left if x in right]

            elif token_type == TokenType.MINUSMINUS:
                output = list(left)
                for v in right:
                    if v in output:
                        output.remove(v)
            else:
                raise TypeError("Something wrong is broken.")

            return output

        if token_type in functions.COMPARISON_OPERATORS:
            if isinstance(right, (int, float)):
                right = [right]
            elif not isinstance(right, list):
                raise TypeError(f"Unexpected type {type(right)}")

            if not isinstance(left, (list, int, float)):
                raise TypeError(f"Unexpected type {type(left)}")

            check = functions.COMPARISON_OPERATORS[token_type]
            return [v for v in right if check(left, v)]

        if isinstance(left, list):
            left = left[0]

        if isinstance(right, list):
            right = right[0]

        if token_type in functions.CALC_OPERATORS:
            func = functions.CALC_OPERATORS[token_type]
            return func(left, right)

        raise functions.UnknownOperator(f"Unknown operator {expr.operator.token_type} in binary expression")

    def visit_Grouping_Expression(self, expr: expression.Grouping):
        return expr.expression.accept(self)

    def visit_Block_Expression(self, expr: expression.Block):
        val = None
        self.push()
        for stmt in expr.statements:
            val = stmt.accept(self)
        self.pop()
        return val

    def visit_Pair_Expression(self, expr: expression.Pair):
        return (expr.first.accept(self), expr.second.accept(self))

    def visit_List_Expression(self, expr: expression.List):
        output: List[Any] = []
        for value in expr.value:
            res = value.accept(self)
            if isinstance(res, list):
                output += res
            else:
                output.append(res)

        return output

    def visit_Assign_Expression(self, expr: expression.Assign):
        value = expr.value.accept(self)

        if not isinstance(expr.name.literal, str):
            raise TypeError("Variable name must be string")

        self.variables[expr.name.literal] = value

    def visit_Variable_Expression(self, expr: expression.Variable):
        if not isinstance(expr.name.literal, str):
            raise TypeError("Variable name must be string")

        return self.variables.get(expr.name.literal, None)

    def visit_Conditional_Expression(self, stmt: expression.Conditional):
        if stmt.condition.accept(self):
            return stmt.truth.accept(self)
        return stmt.falsy.accept(self)

    def visit_Foreach_Expression(self, expr: expression.Foreach):
        output: List[Any] = []
        self.push()

        values = expr.source.accept(self)

        if not isinstance(expr.iterator.name.literal, str):
            raise TypeError("Variable name must be string")

        for val in values:
            self.variables[expr.iterator.name.literal] = val
            output.append(expr.block.accept(self))
        self.pop()
        return output

    def visit_Repeat_Expression(self, stmt: expression.Repeat):
        condition = stmt.condition
        action = stmt.action
        qualifier = stmt.qualifier

        self.push()
        action_variable_name = action.name
        if condition.token_type == TokenType.WHILE:
            res = action.accept(self)
            while qualifier.accept(self) and not self.average:
                res = action.accept(self)

        if condition.token_type == TokenType.UNTIL:
            res = action.accept(self)
            while not qualifier.accept(self) and not self.average:
                res = action.accept(self)

        if not isinstance(action_variable_name.literal, str):
            raise TypeError(f"Expected string, got {action_variable_name.literal}")

        res = self.variables.get(action_variable_name.literal)
        self.pop()
        return res

    def visit_Accumulate_Expression(self, stmt: expression.Accumulate) -> List[Union[str, Number, NumberList, None]]:
        action = stmt.action
        qualifier = stmt.qualifier

        result: List[Union[str, Number, NumberList, None]] = []
        self.push()
        action_variable_name = action.name
        action.accept(self)

        if not isinstance(action_variable_name.literal, str):
            raise TypeError(f"Expected string, got {action_variable_name.literal}")

        result.append(self.variables.get(action_variable_name.literal))

        while qualifier.accept(self):
            action.accept(self)
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
        if not isinstance(stmt.name.literal, str):
            raise TypeError(f"Expected string, got {stmt.name.literal}")

        self.functions[stmt.name.literal] = stmt

    def visit_Compositional_Statement(self, stmt: statement.Compositional):
        if not isinstance(stmt.name.literal, str):
            raise TypeError(f"Expected string, got {stmt.name.literal}")

        self.functions[stmt.name.literal] = stmt

    def visit_Call_Expression(self, expr: expression.Call) -> Any:
        if not isinstance(expr.name.literal, str):
            raise TypeError("Function name must be string")

        stmt = self.functions[expr.name.literal]

        if isinstance(stmt, statement.Compositional):
            return self.call_compositional(expr, stmt)

        return self.call_function(expr, stmt)

    def call_compositional(self, expr: expression.Call, stmt: statement.Compositional):
        self.push()

        res = stmt.empty.value

        parameter = expr.parameters[0]

        if isinstance(parameter, expression.List):
            stmt_operator = stmt.union
            for next_val in parameter.value:
                if isinstance(stmt_operator, Token) and stmt_operator.token_type == TokenType.IDENTIFIER:
                    if not isinstance(res, (str, int, float, type(None))):
                        raise TypeError(f"Unsupported type error: {res}")

                    res = self.visit_Call_Expression(
                        expression.Call(
                            name=stmt_operator,
                            parameters=[expression.Literal(res), next_val],
                        )
                    )
                else:
                    if not isinstance(stmt_operator, Token):
                        raise TypeError(f"Expected Token, got {stmt_operator}")
                    if not isinstance(res, (str, int, float, type(None))):
                        raise TypeError(f"Unsupported type error: {res}")
                    res = self.visit_Binary_Expression(expression.Binary(expression.Literal(res), operator=stmt_operator, right=next_val))
        else:
            stmt_operator = stmt.singleton
            if isinstance(stmt_operator, Token) and stmt_operator.token_type == TokenType.IDENTIFIER:
                res = self.visit_Call_Expression(expression.Call(name=stmt_operator, parameters=[expression.Literal(res)]))
            else:
                if not isinstance(stmt_operator, Token):
                    raise TypeError(f"Expected token, got {stmt_operator}")
                res = self.visit_Unary_Expression(expression.Unary(operator=stmt_operator, right=parameter))

        self.pop()

        if not isinstance(res, (str, int, float)):
            raise TypeError(f"Unexpected type: {type(res)}")
        return res

    def call_function(self, expr: expression.Call, stmt: statement.Function):
        self.push()
        for name, value in zip(stmt.parameters, expr.parameters):
            if not isinstance(name.literal, str):
                raise TypeError("Name of variable must be string")

            self.variables[name.literal] = value.accept(self)

        if isinstance(stmt.expression, statement.Expression):
            res = stmt.expression.accept(self)
            self.pop()
            return res

        res = stmt.accept(self)
        self.pop()
        return res

    def visit_Print_Statement(self, stmt: statement.Print):
        repeats = stmt.repeats
        expr = stmt.expression

        return [str(expr.accept(self)) for _ in range(repeats)]

    def visit_TextAlign_Expression(self, expr: expression.TextAlign):
        align_operator = expr.operator
        left = expr.left.accept(self)
        right = expr.right.accept(self)

        return functions.text_align(left, right, align_operator.lexeme)
