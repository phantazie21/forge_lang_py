from forge_token import ForgeToken, TokenType
from expr import *
from stmt import *
from error import *

class Parser:
    def __init__(self, tokens):
        self.current = 0
        self.tokens = tokens

    def match(self, types):
        for _type in types:
            if self.check(_type):
                self.advance()
                return True
        return False
    
    def check(self, _type):
        if self.isAtEnd():
            return False
        return self.peek().tokenType == _type

    def advance(self):
        if not self.isAtEnd():
            self.current += 1
        return self.previous()
    
    def isAtEnd(self):
        return self.peek().tokenType == TokenType.EOF
    
    def peek(self):
        return self.tokens[self.current]
    
    def previous(self):
        return self.tokens[self.current - 1]

    def expression(self):
        return self.assignment()
    
    def assignment(self):
        expr = self._or()

        if self.match([TokenType.EQUAL]):
            equals = self.previous()
            value = self.assignment()
            if isinstance(expr, Variable):
                name = expr.name
                return Assign(name, value)
            if isinstance(expr, Get):
                get = expr
                return Set(get.object, get.name, value)
            error(equals, "Invalid assignment target.")
        
        return expr
    
    def _or(self):
        expr = self._and()

        while self.match([TokenType.OR]):
            operator = self.previous()
            right = self._and()
            expr = Logical(expr, operator, right)

        return expr
    
    def _and(self):
        expr = self.equality()

        while self.match([TokenType.AND]):
            operator = self.previous()
            right = self.equality()
            expr = Logical(expr, operator, right)

        return expr

    def equality(self):
        expr = self.comparison()
        while self.match([TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL]):
            operator = self.previous()
            right = self.comparison()
            expr = Binary(expr, operator, right)
        
        return expr
    
    def comparison(self):
        expr = self.term()

        while self.match([TokenType.GREATER, TokenType.GREATER_EQUAL, TokenType.LESS, TokenType.LESS_EQUAL]):
            operator = self.previous()
            right = self.term()
            expr = Binary(expr, operator, right)

        return expr
    
    def term(self):
        expr = self.factor()

        while self.match([TokenType.MINUS, TokenType.PLUS]):
            operator = self.previous()
            right = self.factor()
            expr = Binary(expr, operator, right)

        return expr
    
    def factor(self):
        expr = self.unary()

        while self.match([TokenType.SLASH, TokenType.STAR]):
            operator = self.previous()
            right = self.unary()
            expr = Binary(expr, operator, right)

        return expr
    
    def unary(self):
        if self.match([TokenType.BANG, TokenType.MINUS]):
            operator = self.previous()
            right = self.unary()
            return Unary(operator, right)
        
        return self.call()
    
    def call(self):
        expr = self.primary()

        while True:
            if self.match([TokenType.LEFT_PAREN]):
                expr = self.finishCall(expr)
            elif self.match([TokenType.DOT]):
                name = self.consume(TokenType.IDENTIFIER, "Expect property name after '.'.")
                expr = Get(expr, name)
            else:
                break

        return expr
    
    def finishCall(self, callee):
        arguments = []
        if not self.check(TokenType.RIGHT_PAREN):
            while True:
                if len(arguments) >= 255:
                    error(self.peek(), "Can't have more than 255 arguments.")
                arguments.append(self.expression())
                if not self.match([TokenType.COMMA]):
                    break
        paren = self.consume(TokenType.RIGHT_PAREN, "Expect ')' after arguments.")

        return Call(callee, paren, arguments)

    
    def primary(self):
        if self.match([TokenType.FALSE]):
            return Literal(False)
        
        if self.match([TokenType.TRUE]):
            return Literal(True)
        
        if self.match([TokenType.NIL]):
            return Literal(None)
        
        if self.match([TokenType.STRING, TokenType.NUMBER]):
            return Literal(self.previous().literal)
        
        if self.match([TokenType.BREAK]):
            return Literal("Break")
        
        if self.match([TokenType.CONTINUE]):
            return Literal("Continue")
        
        if self.match([TokenType.THIS]):
            return This(self.previous())
        
        if self.match([TokenType.SUPER]):
            keyword = self.previous()
            self.consume(TokenType.DOT, "Expect '.' after 'super'.")
            method = self.consume(TokenType.IDENTIFIER, "Expect superclass method name.")
            return Super(keyword, method)
        
        if self.match([TokenType.IDENTIFIER]):
            return Variable(self.previous())
        
        if self.match([TokenType.LEFT_PAREN]):
            expr = self.expression()
            self.consume(TokenType.RIGHT_PAREN, "Expect ')' after expression.")
            return Grouping(expr)
        
        self.error(self.peek(), "Expect expression.")
        
    def consume(self, _type, message):
        if self.check(_type):
            return self.advance()
        
        self.error(self.peek(), message)

    def error(self, token, message):
        if token.tokenType == TokenType.EOF:
            report(token.line , message, " at end")
            raise Exception()
        else:
            report(token.line, message, f" at '{token.lexeme}' ")
            raise Exception()

    def synchronize(self):
        self.advance()

        while not self.isAtEnd():
            if self.previous().tokenType == TokenType.SEMICOLON:
                return
            if self.peek().tokenType == TokenType.CLASS:
                return
            elif self.peek().tokenType == TokenType.FUN:
                return
            elif self.peek().tokenType == TokenType.VAR:
                return
            elif self.peek().tokenType == TokenType.FOR:
                return
            elif self.peek().tokenType == TokenType.IF:
                return
            elif self.peek().tokenType == TokenType.WHILE:
                return
            elif self.peek().tokenType == TokenType.PRINT:
                return
            elif self.peek().tokenType == TokenType.RETURN:
                return
            elif self.peek().tokenType == TokenType.BREAK:
                return
            self.advance()

    def parse(self):
        statements = []
        while not self.isAtEnd():
            statements.append(self.declaration())
        return statements
    
    def declaration(self):
        try:
            if self.match([TokenType.CLASS]):
                return self.classDeclaration()
            if self.match([TokenType.FUN]):
                return self.function("function")
            if self.match([TokenType.VAR]):
                return self.varDeclaration()
            return self.statement()
        except:
            self.synchronize()
            return None
        
    def classDeclaration(self):
        name = self.consume(TokenType.IDENTIFIER, "Expect class name.")
        superclass = None
        if self.match([TokenType.LESS]):
            self.consume(TokenType.IDENTIFIER, "Expect superclass name.")
            superclass = Variable(self.previous())
        self.consume(TokenType.LEFT_BRACE, "Expect '{' before class body.")
        methods = []
        while not self.check(TokenType.RIGHT_BRACE) and not self.isAtEnd():
            methods.append(self.function("method"))

        self.consume(TokenType.RIGHT_BRACE, "Expect '}' after class body.")
        return Class(name, superclass, methods)
        
    def function(self, kind):
        name = self.consume(TokenType.IDENTIFIER, f"Expect {kind} name.")
        self.consume(TokenType.LEFT_PAREN, f"Expect '(' after {kind} name.")
        parameters = []
        if not self.check(TokenType.RIGHT_PAREN):
            while True:
                if len(parameters) >= 255:
                    error(self.peek(), "Can't have more than 255 arguments.")
                parameters.append(self.consume(TokenType.IDENTIFIER, "Expect parameter name."))
                if not self.match([TokenType.COMMA]):
                    break
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after parameters.")
        self.consume(TokenType.LEFT_BRACE, "Expect '{' before " + kind + " body.")
        body = self.block()
        return Function(name, parameters, body)
        
    def varDeclaration(self):
        name = self.consume(TokenType.IDENTIFIER, "Expect variable name.")
        initializer = None
        if self.match([TokenType.EQUAL]):
            initializer = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after variable declaration.")
        return Var(name, initializer)

    def statement(self):
        if self.match([TokenType.FOR]):
            return self.forStatement()
        if self.match([TokenType.PRINT]):
            return self.printStatement()
        if self.match([TokenType.RETURN]):
            return self.returnStatement()
        if self.match([TokenType.WHILE]):
            return self.whileStatement()
        if self.match([TokenType.LEFT_BRACE]):
            return Block(self.block())
        if self.match([TokenType.IF]):
            return self.ifStatement()
        if self.match([TokenType.BREAK]):
            return self.breakStatement()
        if self.match([TokenType.CONTINUE]):
            return self.continueStatement()
        return self.expressionStatement()
    
    def returnStatement(self):
        keyword = self.previous()
        value = None
        if not self.check(TokenType.SEMICOLON):
            value = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after return value.")
        return Return(keyword, value)

    def forStatement(self):
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'for'.")
        initializer = None
        if self.match([TokenType.VAR]):
            initializer = self.varDeclaration()
        else:
            initializer = self.expressionStatement()
        
        condition = None
        if not self.check(TokenType.SEMICOLON):
            condition = self.expression()
        
        self.consume(TokenType.SEMICOLON, "Expect ';' after loop condition.")

        increment = None
        if not self.check(TokenType.RIGHT_PAREN):
            increment = self.expression()

        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after for clauses.")
        body = self.statement()

        if increment != None:
            body = Block([body, Expression(increment)])

        if condition == None:
            condition = Literal(True)

        whileStmt = While(condition, body)
        if increment != None:
            whileStmt.increment = increment

        if initializer != None:
            body = Block([initializer, whileStmt])
        else:
            body = whileStmt

        return body

    def whileStatement(self):
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'while'.")
        condition = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after while condition.")
        body = self.statement()
        return While(condition, body)

    def block(self):
        statements = []
        while not self.check(TokenType.RIGHT_BRACE) or self.isAtEnd():
            statements.append(self.declaration())
        
        self.consume(TokenType.RIGHT_BRACE, "Expect '}' after block.")
        return statements

    def printStatement(self):
        value = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after value.")
        return Print(value)
    
    def expressionStatement(self):
        expr = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after expression.")
        return Expression(expr)
    
    def ifStatement(self):
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'if'.")
        condition = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after if condition.")

        thenBranch = self.statement()
        elseBranch = None
        if self.match([TokenType.ELSE]):
            elseBranch = self.statement()
        
        return If(condition, thenBranch, elseBranch)

    def breakStatement(self):
        self.consume(TokenType.SEMICOLON, "Expect ';' after 'break'.")
        return Break(self.previous())

    def continueStatement(self):
        self.consume(TokenType.SEMICOLON, "Expect ';' after 'continue'.")
        return Continue(self.previous())