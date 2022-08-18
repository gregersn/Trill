"""Parser code."""
from typing import Any, List, Union

from .tokens import Token, TokenType
from .ast import expression
from .ast import statement


class Parser:
    """Basic Troll parser."""
    tokens: List[Token]
    current: int = 0

    def __init__(self, tokens: List[Token]):
        self.tokens = tokens

    def __repr__(self):
        return f"<Parser {self.current} / {len(self.tokens)}>"

    def is_at_end(self):
        # Check if end of source is reached.
        return self.peek().token_type == TokenType.EOF

    def peek(self, lookahead: int = 0):
        return self.tokens[self.current + lookahead]

    def previous(self):
        return self.tokens[self.current - 1]

    def check(self, _type: TokenType):
        if self.is_at_end():
            return False
        return self.peek().token_type == _type

    def advance(self):
        if not self.is_at_end():
            self.current += 1

        return self.previous()

    def match(self, *types: TokenType):
        for _type in types:
            if self.check(_type):
                self.advance()
                return True
        return False

    def error(self, token: Token, message: str):
        return Exception(f"{str(token)}: {message}")

    def consume(self, _type: TokenType, message: str):
        if self.check(_type):
            return self.advance()
        raise self.error(self.peek(), message)

    def parse(self):
        # roll ->  (function* | expression)
        statements: List[Union[statement.Statement, expression.Expression]] = []
        while not self.is_at_end():
            expr = self.declaration()
            statements.append(expr)
        return statements

    def declaration(self) -> Union[statement.Statement, expression.Expression]:
        # statement -> exprStatement | printStatement;
        # if self.match(TokenType.PRINT):
        #     return self.print_Statement()
        if self.match(TokenType.FUNCTION):
            return self.function_declaration()

        expr = self.parse_expression()

        if self.check(TokenType.SEMICOLON):
            expressions = [expr]
            while self.match(TokenType.SEMICOLON):
                expr = self.parse_expression()
                expressions.append(expr)

            return expression.Block(expressions)

        return expr

    def if_expression(self):
        condition = self.parse_expression()
        self.consume(TokenType.THEN, "Missing THEN after condition")
        true_result = self.parse_expression()
        self.consume(TokenType.ELSE, "Missing ELSE after true result")
        false_result = self.parse_expression()

        return expression.Conditional(condition, true_result, false_result)

    def foreach_expression(self):
        iterator = self.primary()
        self.consume(TokenType.IN, 'Expecting IN')
        source = self.parse_expression()
        self.consume(TokenType.DO, "Expected DO")
        block = self.parse_expression()

        assert isinstance(iterator, expression.Variable)

        return expression.Foreach(iterator, source, block)

    def repeat_expression(self):
        action = self.assignment()
        if not self.match(TokenType.WHILE, TokenType.UNTIL):
            raise Exception("Wtf")
        condition = self.previous()
        qualifier = self.parse_expression()

        assert isinstance(action, expression.Assign), action

        return expression.Repeat(condition, action, qualifier)

    def accumulate_expression(self):
        action = self.assignment()
        self.consume(TokenType.WHILE, "Expect a clause in accumulation")
        qualifier = self.parse_expression()
        assert isinstance(action, expression.Assign)
        return expression.Accumulate(action, qualifier)

    def function_declaration(self) -> statement.Function:
        identifier = self.consume(TokenType.IDENTIFIER, "Expected function identifier.")

        self.consume(TokenType.LPAREN, "Expect '(' after function name.")
        parameters: List[Token] = []
        while not self.match(TokenType.RPAREN):
            parameters.append(self.consume(TokenType.IDENTIFIER, "Expect variable name"))

        self.consume(TokenType.EQUAL, "Expect '=' before function body.")
        expr = self.declaration()

        return statement.Function(identifier, parameters, expr)

    def parse_expression(self) -> expression.Expression:
        if self.match(TokenType.IF):
            return self.if_expression()
        if self.match(TokenType.ACCUMULATE):
            return self.accumulate_expression()
        if self.match(TokenType.REPEAT):
            return self.repeat_expression()
        if self.match(TokenType.FOREACH):
            return self.foreach_expression()

        return self.assignment()

    def function_call(self):
        name = self.consume(TokenType.IDENTIFIER, "Expected name of function to call.")
        parameters: List[expression.Expression] = []
        self.consume(TokenType.LPAREN, "Expect parenthesis for function call")
        while not self.match(TokenType.RPAREN):
            parameters.append(self.parse_expression())

        return expression.Call(name, parameters)

    def assignment(self) -> expression.Expression:
        expr = self.comparison()

        if self.match(TokenType.ASSIGN):
            _ = self.previous()
            value = self.assignment()

            if isinstance(expr, expression.Variable):
                name = expr.name
                return expression.Assign(name, value)

        return expr

    def comparison(self) -> expression.Expression:
        expr = self.term()
        while False:  # Currently not in use.
            operator = self.previous()
            right = self.term()
            expr = expression.Binary(expr, operator, right)

        return expr

    def term(self) -> expression.Expression:
        expr = self.factor()
        while self.match(
                TokenType.DROP,
                TokenType.KEEP,
                TokenType.MINUS,
                TokenType.MINUSMINUS,
                TokenType.PICK,
                TokenType.PLUS,
                TokenType.RANGE,
                TokenType.UNION,
                TokenType.AND,
                TokenType.DEFAULT,
        ):
            operator = self.previous()
            right = self.factor()
            expr = expression.Binary(expr, operator, right)
        return expr

    def factor(self) -> expression.Expression:
        expr = self.unary()

        while self.match(TokenType.DIVIDE, TokenType.MULTIPLY):
            operator = self.previous()
            right = self.unary()
            expr = expression.Binary(expr, operator, right)

        return expr

    def unary(self) -> expression.Expression:
        if self.match(TokenType.CALL):
            return self.function_call()

        operators = [
            TokenType.CHOOSE,
            TokenType.COUNT,
            TokenType.DIFFERENT,
            TokenType.MAX,
            TokenType.MAXIMAL,
            TokenType.MEDIAN,
            TokenType.MIN,
            TokenType.MINIMAL,
            TokenType.MINUS,
            TokenType.SIGN,
            TokenType.SUM,
            TokenType.PROBABILITY,
            TokenType.NOT,
        ]
        if self.match(*operators):
            operator = self.previous()
            right = self.unary()
            return expression.Unary(operator, right)

        return self.filter()

    def filter(self):
        expr = self.samples()
        while self.match(
                TokenType.LESS_THAN,
                TokenType.GREATER_THAN,
                TokenType.LESS_THAN_OR_EQUAL,
                TokenType.GREATER_THAN_OR_EQUAL,
                TokenType.EQUAL,
                TokenType.NOT_EQUAL,
        ):
            operator = self.previous()
            right = self.factor()
            expr = expression.Binary(expr, operator, right)

        return expr

    def samples(self) -> expression.Expression:
        expr = self.diceroll()

        if self.match(TokenType.SAMPLES):
            operator = self.previous()
            right = self.parse_expression()
            expr = expression.Binary(expr, operator, right)

        return expr

    def diceroll(self) -> expression.Expression:
        # A single die
        if self.match(TokenType.DICE):
            operator = self.previous()
            right = self.primary()
            return expression.Unary(operator, right)

        expr = self.primary()

        # Multiple dice
        if self.match(TokenType.DICE):
            operator = self.previous()
            right = self.primary()
            expr = expression.Binary(expr, operator, right)

        return expr

    def primary(self):
        if self.match(TokenType.INTEGER, TokenType.FLOAT):
            return expression.Literal(self.previous().literal)

        if self.match(TokenType.IDENTIFIER):
            return expression.Variable(self.previous())

        if self.match(TokenType.LPAREN):
            expr = self.parse_expression()
            if self.match(TokenType.RPAREN):
                return expression.Grouping(expr)

            self.consume(TokenType.SEMICOLON, "Expected a semi colon")
            statements: List[expression.Expression] = [expr]
            while not self.match(TokenType.RPAREN):
                statements.append(self.parse_expression())

            return expression.Block(statements)

        if self.match(TokenType.LBRACKET):
            elements: List[Any] = []
            while not self.check(TokenType.RBRACKET):
                elements.append(self.parse_expression())
                if not self.check(TokenType.RBRACKET):
                    self.consume(TokenType.COMMA, "Expect ',' to separate elements.")
            self.consume(TokenType.RBRACKET, "Missing '}' to close list.")
            return expression.List(elements)

        if self.match(TokenType.LSQUARE):
            a = self.parse_expression()
            self.consume(TokenType.COMMA, "Expect ',' to separate pair.")
            b = self.parse_expression()
            self.consume(TokenType.RSQUARE, "Missing ']' to close pair.")
            return expression.Pair(a, b)

        raise Exception(f"Unexpected token: {self.peek().token_type.value}")
