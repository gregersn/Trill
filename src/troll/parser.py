"""Parser code."""
from typing import List

from troll.tokens import Token, TokenType
from troll.ast import expression
from troll.ast import statement

# Precedence: Order of evaluation of operators. Higher precendence evaulated first.
# Associativity: In series of same operator, order of operation, from left or from right
# Separate rule for each precedence level.


class Parser:
    """Basic Troll parser."""
    tokens: List[Token]
    current: int = 0

    def __init__(self, tokens: List[Token]):
        self.tokens = tokens

    def is_at_end(self):
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

    def program(self):
        # program -> statement* EOF ;
        ...

    def parse_statement(self) -> statement.Statement:
        # statement -> exprStatement | printStatement;
        # if self.match(TokenType.PRINT):
        #     return self.print_Statement()
        return self.expression_statement()

    def expression_statement(self) -> statement.Statement:
        # exprStatement -> expression ";"|EOF ;
        expr = self.parse_expression()
        if self.check(TokenType.EOF):
            self.consume(TokenType.SEMICOLON, "Expect ';' after expression.")
        return statement.Expression(expr)

    def print_statement(self):
        # printStatement -> "print" expression ";"|EOF ;
        ...

    def parse_expression(self) -> expression.Expression:
        # expression
        # equality (==, !=)
        # comparison (>, >=, <, <=)
        # term (-, +)
        # factor (/, *)
        # unary (!, -)
        # primary

        expr = self.comparison()
        while self.match(TokenType.EQUAL):
            operator = self.previous()
            right = self.comparison()
            expr = expression.Binary(expr, operator, right)

        return expr

    def parse(self):
        statements: List[statement.Statement] = []
        while not self.is_at_end():
            statements.append(self.parse_statement())
        return statements

    def comparison(self) -> expression.Expression:
        expr = self.term()
        while self.match(TokenType.LESS_THAN, TokenType.GREATER_THAN):
            operator = self.previous()
            right = self.term()
            expr = expression.Binary(expr, operator, right)

        return expr

    def term(self) -> expression.Expression:
        expr = self.factor()
        while self.match(TokenType.MINUS, TokenType.PLUS, TokenType.SAMPLES, TokenType.UNION):
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
        operators = [TokenType.MINUS, TokenType.SUM, TokenType.SIGN]
        if self.match(*operators):
            operator = self.previous()
            right = self.unary()
            return expression.Unary(operator, right)

        return self.diceroll()

    def diceroll(self) -> expression.Expression:
        # A single die
        if self.check(TokenType.DICE):
            operator = self.advance()
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
        if self.match(TokenType.NUMBER):
            return expression.Literal(self.previous().literal)

        if self.match(TokenType.LPAREN):
            expr = self.parse_expression()
            self.consume(TokenType.RPAREN, "Expect ')' after espression.")
            return expression.Grouping(expr)

        raise Exception(f"Unexpected token: {self.peek()}")
