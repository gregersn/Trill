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
        statements: List[Union[statement.Statement, expression.Expression]] = []
        while not self.is_at_end():
            if self.match(TokenType.COMMENT):
                continue
            statements.append(self.declaration())
        return statements

    def declaration(self) -> Union[statement.Statement, expression.Expression]:
        # statement -> exprStatement | printStatement;
        # if self.match(TokenType.PRINT):
        #     return self.print_Statement()
        if self.check(TokenType.IDENTIFIER) and self.peek(1).token_type == TokenType.ASSIGN:
            return self.declaration_statement()
        return self.parse_statement()

    def if_expression(self):
        condition = self.parse_expression()
        self.consume(TokenType.THEN, "Missing THEN after condition")
        true_result = self.parse_expression()
        self.consume(TokenType.ELSE, "Missing ELSE after true result")
        false_result = self.parse_expression()

        return expression.Conditional(condition, true_result, false_result)

    def foreach_statement(self):
        iterator = self.primary()
        self.consume(TokenType.IN, 'Expecting IN')
        source = self.parse_expression()
        self.consume(TokenType.DO, "Expected DO")
        block = self.parse_expression()

        assert isinstance(iterator, expression.Variable)

        return statement.Foreach(iterator, source, block)

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

    def parse_statement(self) -> Union[statement.Statement, expression.Expression]:
        if self.match(TokenType.FOREACH):
            return self.foreach_statement()
        return self.expression_statement()

    def block(self) -> Union[statement.Statement, expression.Expression]:
        stmt = self.declaration()

        if self.match(TokenType.SEMICOLON):
            statements: List[statement.Statement] = [stmt]
            while not self.match(TokenType.RPAREN):
                statements.append(self.declaration())
            return statement.Block(statements)

        self.consume(TokenType.RPAREN, "Expected closing parentheis.")
        assert isinstance(stmt, expression.Expression)
        return expression.Grouping(stmt)

    def declaration_statement(self) -> statement.Variable:
        # identifier := expression ";"|EOF ;
        identifier = self.consume(TokenType.IDENTIFIER, "Variable identifier.")
        self.consume(TokenType.ASSIGN, "Assignment operator.")
        expr = self.parse_expression()
        if not self.is_at_end():
            self.consume(TokenType.SEMICOLON, "Expect ';' after expression.")
        return statement.Variable(identifier, expr)

    def expression_statement(self) -> Union[statement.Statement, expression.Expression]:
        # exprStatement -> expression ";"|EOF ;
        expr = self.parse_expression()

        if self.match(TokenType.SEMICOLON):
            return statement.Expression(expr)

        return expr

    def print_statement(self):
        # printStatement -> "print" expression ";"|EOF ;
        ...

    def parse_expression(self) -> expression.Expression:
        if self.match(TokenType.IF):
            return self.if_expression()
        if self.match(TokenType.ACCUMULATE):
            return self.accumulate_expression()
        if self.match(TokenType.REPEAT):
            return self.repeat_expression()

        return self.assignment()

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
                if not self.peek().token_type == TokenType.RPAREN:
                    self.consume(TokenType.SEMICOLON, "Expected a semi colon")

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
