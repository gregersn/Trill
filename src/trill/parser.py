"""Parser code."""
from typing import Any, List, Optional, Union

from .tokens import Token, TokenType
from .ast import expression
from .ast import statement
from .error import handler as error_handler, ParserError


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
        """Check next token.
        Return True if next token is of type _type
        """
        if self.is_at_end():
            return False
        return self.peek().token_type == _type

    def advance(self):
        if not self.is_at_end():
            self.current += 1

        return self.previous()

    def match(self, *types: TokenType):
        """Check and consume a token of given types."""
        for _type in types:
            if self.check(_type):
                self.advance()
                return True
        return False

    def error(self, message: str):
        token = self.tokens[self.current]
        error_handler.report(ParserError(token.line, token.column, message))

    def consume(self, _type: TokenType, message: str):
        if self.check(_type):
            return self.advance()
        self.error(message)

    def parse(self):
        # roll ->  (function* | expression)
        statements: List[Union[statement.Statement,
                               expression.Expression]] = []
        while not self.is_at_end():
            expr = self.declaration()
            if expr:
                statements.append(expr)

            if expr is None and error_handler.had_error:
                break

        return statements

    def print_statement(self):
        if self.match(TokenType.INTEGER):
            repeats = self.previous().literal
        else:
            repeats = 1

        self.consume(TokenType.TEXTBOX, 'Expected a string operator.')
        if not isinstance(repeats, int):
            self.error(f"Type error: expected int, got {type(repeats)}")
            return None

        return statement.Print(self.parse_expression(), repeats)

    def declaration(self) -> Optional[Union[statement.Statement, expression.Expression]]:
        # statement -> exprStatement | printStatement;

        if self.match(TokenType.COMPOSITIONAL):
            return self.compositional_declaration()

        if self.match(TokenType.FUNCTION):
            return self.function_declaration()

        if (self.check(TokenType.INTEGER) and self.peek(1).token_type == TokenType.TEXTBOX) or self.check(TokenType.TEXTBOX):
            return self.print_statement()

        expr = self.parse_expression()

        if expr is None:
            return None

        if self.check(TokenType.TEXTALIGN):
            while self.match(TokenType.TEXTALIGN):
                operator = self.previous()
                right = self.declaration()
                assert right is not None
                expr = expression.TextAlign(expr, operator, right)
            return expr

        if self.check(TokenType.SEMICOLON):
            expressions = [expr]
            if self.check(TokenType.SEMICOLON) and not isinstance(expr, expression.Assign):
                token = self.tokens[self.current]
                self.error(f"Unexpected semicolon: {token.lexeme}")

            while self.match(TokenType.SEMICOLON):
                if not isinstance(expr, expression.Assign):
                    token = self.tokens[self.current]
                    self.error(f"Expected assignment, got: {token.lexeme}")

                expr = self.parse_expression()

                if expr:
                    expressions.append(expr)

            return expression.Block(expressions)

        return expr

    def if_expression(self):
        condition = self.parse_expression()
        self.consume(TokenType.THEN, "Missing THEN after condition")
        true_result = self.parse_expression()
        self.consume(TokenType.ELSE, "Missing ELSE after true result")
        false_result = self.parse_expression()

        err = False

        if not condition:
            self.error("Missing condition in if expression")
            err = True

        if not true_result:
            self.error("Missing positive result in if-expression")
            err = True

        if not false_result:
            self.error("Missing negative result in if-expression")
            err = True

        if err:
            return None

        return expression.Conditional(condition, true_result, false_result)

    def foreach_expression(self):
        iterator = self.primary()
        self.consume(TokenType.IN, 'Expecting IN')
        source = self.parse_expression()
        self.consume(TokenType.DO, "Expected DO")
        block = self.parse_expression()

        err = False

        if not isinstance(iterator, expression.Variable):
            self.error(
                f"Expected iterator to be a variable, got {type(expression.Variable)}")
            err = True

        if not source:
            self.error("Missing loop source")
            err = True

        if not block:
            self.error("Missing loop block")
            err = True

        if err:
            return None

        return expression.Foreach(iterator, source, block)

    def repeat_expression(self):
        action = self.assignment()
        if not self.match(TokenType.WHILE, TokenType.UNTIL):
            token = self.tokens[self.current]
            self.error(f"Expected WHILE or UNTIL, got {token.token_type}")
            return None
        condition = self.previous()
        qualifier = self.parse_expression()

        if qualifier is None:
            token = self.tokens[self.current]
            self.error("Missing qualifier in repeat-expression")
            return None

        if not isinstance(action, expression.Assign):
            self.error(f"Expected assignment, got {action}")
            return None

        return expression.Repeat(condition, action, qualifier)

    def accumulate_expression(self):
        action = self.assignment()
        self.consume(TokenType.WHILE, "Expect a clause in accumulation")
        qualifier = self.parse_expression()

        err = None
        if not isinstance(action, expression.Assign):
            self.error(f"Expected assignment, got {action}")
            err = True

        if not qualifier:
            self.error("Missing qualifier")
            err = True

        if err:
            return None

        return expression.Accumulate(action, qualifier)

    def function_declaration(self) -> Optional[statement.Function]:
        identifier = self.consume(
            TokenType.IDENTIFIER, "Expected function identifier.")

        self.consume(TokenType.LPAREN, "Expect '(' after function name.")
        parameters: List[Token] = []
        err = False
        while not self.match(TokenType.RPAREN):
            token = self.consume(TokenType.IDENTIFIER, "Expect variable name")
            if not token:
                self.error(f"Expected token, got {token}")
                err = True
            else:
                parameters.append(token)
            self.match(TokenType.COMMA)

        self.consume(TokenType.EQUAL, "Expect '=' before function body.")
        expr = self.declaration()

        if not identifier:
            self.error("Missing expected identifier")
            return None

        if not expr:
            self.error("Missing expected expression")
            return None

        if err:
            return None

        return statement.Function(identifier, parameters, expr)

    def compositional_declaration(self) -> Optional[statement.Compositional]:
        identifier = self.consume(
            TokenType.IDENTIFIER, "Expected compositional identifier.")

        self.consume(TokenType.LPAREN, "Expect '(' after compositional name.")
        empty = self.primary()
        self.consume(TokenType.COMMA, "Expected comma")
        singleton = self.tokens[self.current]
        self.consume(singleton.token_type, "Found one")
        self.consume(TokenType.COMMA, "Expected comma")
        union = self.tokens[self.current]
        self.consume(union.token_type, "Expected identifier")
        self.consume(TokenType.RPAREN, "Expect ')' after last compositional parameter.")

        return statement.Compositional(identifier, empty, singleton, union)

    def parse_expression(self) -> Optional[expression.Expression]:
        if self.match(TokenType.IF):
            return self.if_expression()
        if self.match(TokenType.ACCUMULATE):
            return self.accumulate_expression()
        if self.match(TokenType.REPEAT):
            return self.repeat_expression()
        if self.match(TokenType.FOREACH):
            return self.foreach_expression()

        return self.assignment()

    def selection_expression(self):
        """Handle LEAST and LARGEST."""
        selector = self.previous()
        count = self.parse_expression()
        selection = self.diceroll()

        if error_handler.had_error:
            return None

        if not count:
            self.error("Missing count in selection expression")
            return None

        if not selection:
            self.error("Missing selection")
            return None

        return expression.Binary(count, selector, selection)

    def function_call(self):
        name = self.consume(TokenType.IDENTIFIER,
                            "Expected name of function to call.")

        parameters: List[expression.Expression] = []
        self.consume(TokenType.LPAREN, "Expect parenthesis for function call")
        while not self.match(TokenType.RPAREN):
            expr = self.parse_expression()
            if expr is None:
                break
            parameters.append(expr)
            self.match(TokenType.COMMA)

        if not name:
            self.error("Missing function name")
            return None

        return expression.Call(name, parameters)

    def assignment(self) -> Optional[expression.Expression]:
        expr = self.comparison()
        if expr is None:
            return None

        if self.match(TokenType.ASSIGN):
            _ = self.previous()
            value = self.assignment()

            if isinstance(expr, expression.Variable):
                name = expr.name
                if not value:
                    self.error("Missing value in assignment")
                    return None

                return expression.Assign(name, value)

        return expr

    def comparison(self) -> Optional[expression.Expression]:
        expr = self.picker()
        while self.match(TokenType.RANGE, TokenType.DEFAULT):
            operator = self.previous()
            right = self.picker()

            if not expr:
                self.error("Missing left hand expression in comparison.")
                return None

            if not right:
                self.error("Missing right hand expression in comparison.")
                return None

            expr = expression.Binary(expr, operator, right)

        return expr

    def picker(self) -> Optional[expression.Expression]:
        expr = self.combination()

        # Left grouping operators.
        while self.match(TokenType.DROP, TokenType.KEEP, TokenType.PICK, TokenType.MINUSMINUS):
            operator = self.previous()
            right = self.combination()

            if not expr:
                self.error("Missing left hand expression in picker.")
                return None

            if not right:
                self.error("Missing right hand expression in picker.")
                return None

            expr = expression.Binary(expr, operator, right)
        return expr

    def combination(self) -> Optional[expression.Expression]:
        expr = self.term()

        # Right grouping operators.
        while self.match(TokenType.UNION, TokenType.AND):
            operator = self.previous()
            right = self.term()

            if not expr:
                self.error("Missing left hand expression in combination.")
                return None

            if not right:
                self.error("Missing right hand expression in combination.")
                return None

            expr = expression.Binary(expr, operator, right)
        return expr

    def term(self) -> Optional[expression.Expression]:
        expr = self.factor()

        # Left grouping operators.
        while self.match(TokenType.PLUS, TokenType.MINUS):
            operator = self.previous()
            right = self.factor()

            if not expr:
                self.error("Missing left hand expression in term.")
                return None

            if not right:
                self.error("Missing right hand expression in term.")
                return None

            expr = expression.Binary(expr, operator, right)
        return expr

    def factor(self) -> Optional[expression.Expression]:
        expr = self.unary()

        # Left grouping operators.
        while self.match(TokenType.DIVIDE, TokenType.MULTIPLY, TokenType.MODULO):
            operator = self.previous()
            right = self.unary()

            if not expr:
                self.error("Missing left hand expression in factor.")
                return None

            if not right:
                self.error("Missing right hand expression in factor.")
                return None

            expr = expression.Binary(expr, operator, right)

        return expr

    def unary(self) -> Optional[expression.Expression]:
        if self.match(TokenType.CALL):
            return self.function_call()

        operators = [
            TokenType.MINUS,
            TokenType.PROBABILITY,
        ]
        if self.match(*operators):
            operator = self.previous()
            qualifier = self.qualifier()

            if not qualifier:
                self.error("Missing qualifier")
                return None

            return expression.Unary(operator, qualifier)

        return self.qualifier()

    def qualifier(self) -> Optional[expression.Expression]:
        # Prefix operators.
        dual_operators = [
            TokenType.LEAST,
            TokenType.LARGEST,
        ]

        if self.match(*dual_operators):
            return self.selection_expression()

        # Prefix operators.
        operators = [
            TokenType.CHOOSE,
            TokenType.COUNT,
            TokenType.SUM,
            TokenType.SIGN,
            TokenType.MIN,
            TokenType.MAX,
            TokenType.DIFFERENT,
            TokenType.MINIMAL,
            TokenType.MAXIMAL,
            TokenType.MEDIAN,
            TokenType.PAIR_VALUE,
            TokenType.NOT,
        ]
        if self.match(*operators):
            operator = self.previous()
            qualifier = self.qualifier()
            if not qualifier:
                self.error("Missing qualifier")
                return None

            return expression.Unary(operator, qualifier)

        return self.filter()

    def filter(self):
        expr = self.samples()

        # Right grouping operators.
        while self.match(
                TokenType.EQUAL,
                TokenType.LESS_THAN,
                TokenType.GREATER_THAN,
                TokenType.LESS_THAN_OR_EQUAL,
                TokenType.GREATER_THAN_OR_EQUAL,
                TokenType.NOT_EQUAL,
        ):
            operator = self.previous()
            factor = self.factor()
            if not factor:
                self.error("Missing factor")
                return None

            expr = expression.Binary(expr, operator, factor)

        return expr

    def samples(self) -> Optional[expression.Expression]:
        expr = self.diceroll()

        if self.match(TokenType.SAMPLES):
            operator = self.previous()
            right = self.parse_expression()

            if not expr:
                self.error("Missing left hand expression in samples.")
                return None

            if not right:
                self.error("Missing right hand expression in samples.")
                return None

            expr = expression.Binary(expr, operator, right)

        return expr

    def diceroll(self) -> Optional[expression.Expression]:
        expr = self.single_roll()

        # Multiple dice
        if self.match(TokenType.DICE):
            operator = self.previous()
            right = self.single_roll()

            if not expr:
                self.error("Missing left hand expression in diceroll.")
                return None

            if not right:
                self.error("Missing right hand expression in diceroll.")
                return None

            expr = expression.Binary(expr, operator, right)

        return expr

    def single_roll(self) -> Optional[expression.Expression]:
        if self.match(TokenType.DICE):
            operator = self.previous()
            right = self.primary()

            if not right:
                self.error("Missing dice size")
                return None

            return expression.Unary(operator, right)

        res = self.primary()

        return res

    def primary(self):
        if self.match(TokenType.INTEGER, TokenType.FLOAT, TokenType.STRING):
            return expression.Literal(self.previous().literal)

        if self.match(TokenType.IDENTIFIER):
            return expression.Variable(self.previous())

        if self.match(TokenType.LPAREN):
            expr = self.parse_expression()

            if not expr:
                self.error("Missing expression")
                return None

            if self.match(TokenType.RPAREN):
                return expression.Grouping(expr)

            self.consume(TokenType.SEMICOLON, "Expected a semi colon")
            if error_handler.had_error:
                return None

            statements: List[expression.Expression] = [expr]
            while not self.match(TokenType.RPAREN):
                expr = self.parse_expression()

                if not expr:
                    self.error("Invalid expression.")
                    return None

                statements.append(expr)

            return expression.Block(statements)

        if self.match(TokenType.LBRACKET):
            elements: List[Any] = []
            while not self.check(TokenType.RBRACKET):
                elements.append(self.parse_expression())
                if not self.check(TokenType.RBRACKET):
                    self.consume(TokenType.COMMA,
                                 "Expect ',' to separate elements.")
            self.consume(TokenType.RBRACKET, "Missing '}' to close list.")
            return expression.List(elements)

        if self.match(TokenType.LSQUARE):
            a = self.parse_expression()

            self.consume(TokenType.COMMA, "Expect ',' to separate pair.")
            b = self.parse_expression()

            self.consume(TokenType.RSQUARE, "Missing ']' to close pair.")

            err = False
            if a is None:
                self.error("Missing first part of pair")
                err = True

            if a is None:
                self.error("Missing second part of pair")
                err = True

            if err:
                return None

            assert a
            assert b

            return expression.Pair(a, b)

        token = self.tokens[self.current]
        self.error(f"Unexpected token: '{token.lexeme}'")
