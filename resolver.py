from collections import deque
from stmt import *
from expr import *
from error import error_token
from enum import Enum, auto

class ClassType(Enum):
    NONE = auto()
    CLASS = auto()
    SUBCLASS = auto()

class FunctionType(Enum):
    NONE = auto()
    FUNCTION = auto()
    INITIALIZER = auto()
    METHOD = auto()

class Resolver:
    def __init__(self, interpreter):
        self.interpreter = interpreter
        self.scopes : deque[dict[str, bool]] = deque()
        self.currentFunction = FunctionType.NONE
        self.currentClass = ClassType.NONE

    def visitBlock(self, blockStatement):
        self.beginScope()
        self.resolveStatements(blockStatement.statements)
        self.endScope()
        return None
    
    def resolveStatements(self, statements):
        for stmt in statements:
            self.resolve(stmt)
    
    def resolve(self, stmt):
        stmt.accept(self)

    def beginScope(self):
        self.scopes.append({})

    def endScope(self):
        self.scopes.pop()

    def visitVar(self, varStatement):
        self.declare(varStatement.name)
        if varStatement.initializer != None:
            self.resolve(varStatement.initializer)
        self.define(varStatement.name)
        return None
    
    def declare(self, name):
        if self.scopes:
            scope = self.scopes[-1]
            if name.lexeme in scope.keys():
                error_token(name, "Already a variable with this name in this scope.")
            scope |= {name.lexeme: False}

    def define(self, name):
        if self.scopes:
            self.scopes[-1] |= {name.lexeme: True}
    
    def visitVariable(self, varExpr):
        if self.scopes and self.scopes[-1].get(varExpr.name.lexeme) is False:
            error_token(varExpr.name, "Can't read local variable in its own initializer.")
        self.resolveLocal(varExpr, varExpr.name)
        return None
    
    def resolveLocal(self, expr, name):
        for i in range(len(self.scopes) - 1, -1, -1):
            if name.lexeme in self.scopes[i]:
                self.interpreter.resolve(expr, len(self.scopes) - 1 - i)
                return
            
    def visitAssign(self, expr):
        self.resolve(expr.value)
        self.resolveLocal(expr, expr.name)
        return None
    
    def visitFunction(self, functionStatement):
        self.declare(functionStatement.name)
        self.define(functionStatement.name)

        self.resolveFunction(functionStatement, FunctionType.FUNCTION)
        return None
    
    def resolveFunction(self, function, _type):
        enclosingFunction = self.currentFunction
        self.currentFunction = _type
        self.beginScope()
        for param in function.params:
            self.declare(param)
            self.define(param)
        
        self.resolveStatements(function.body)
        self.endScope()
        self.currentFunction = enclosingFunction

    def visitExpression(self, stmt):
        self.resolve(stmt.expr)
        return None
    
    def visitIf(self, stmt):
        self.resolve(stmt.condition)
        self.resolve(stmt.thenBranch)
        if self.elseBranch != None:
            self.resolve(stmt.elseBranch)
        return None
    
    def visitPrint(self, stmt):
        self.resolve(stmt.expr)

    def visitReturn(self, stmt):
        if self.currentFunction == FunctionType.NONE:
            error_token(stmt.keyword, "Can't return from top-level code.")

        if stmt.value != None:
            if self.currentFunction == FunctionType.INITIALIZER:
                error_token(stmt.keyword, "Can't return a value from an initializer.")
            self.resolve(stmt.value)

        return None
    
    def visitWhile(self, stmt):
        self.resolve(stmt.condition)
        self.resolve(stmt.body)
        return None
    
    def visitBinary(self, expr):
        self.resolve(expr.expr_left)
        self.resolve(expr.expr_right)
        return None
    
    def visitCall(self, expr):
        self.resolve(expr.callee)

        for argument in expr.args:
            self.resolve(argument)

        return None
    
    def visitGrouping(self, expr):
        self.resolve(expr.expr_expression)
        return None
    
    def visitLiteral(self, expr):
        return None
    
    def visitLogical(self, expr):
        self.resolve(expr.left)
        self.resolve(expr.right)
        return None
    
    def visitUnary(self, expr):
        self.resolve(expr.expr_right)
        return None
    
    def visitClass(self, stmt):
        enclosingClass = self.currentClass
        self.currentClass = ClassType.CLASS
        self.declare(stmt.name)
        self.define(stmt.name)

        if stmt.superclass is not None:
            if stmt.name.lexeme == stmt.superclass.name.lexeme:
                error_token(stmt.superclass.name, "A class can't inherit from itself.")
            self.currentClass = ClassType.SUBCLASS
            self.resolve(stmt.superclass)
            self.beginScope()
            self.scopes[-1] |= {"super": True}

        self.beginScope()
        self.scopes[-1] |= {"this": True}

        for method in stmt.methods:
            declaration = FunctionType.METHOD
            if method.name.lexeme == "init":
                declaration = FunctionType.INITIALIZER
            self.resolveFunction(method, declaration)

        self.endScope()

        if stmt.superclass is not None:
            self.endScope()

        self.currentClass = enclosingClass
        return None
    
    def visitGet(self, expr):
        self.resolve(expr.object)
        return None
    
    def visitSet(self, expr):
        self.resolve(expr.value)
        self.resolve(expr.object)
        return None
    
    def visitThis(self, expr):
        if self.currentClass == ClassType.NONE:
            error_token(expr.keyword, "Can't use 'this' outside of a class.")
            return None
        self.resolveLocal(expr, expr.keyword)
        return None
    
    def visitSuper(self, expr):
        if self.currentClass == ClassType.NONE:
            error_token(expr.keyword, "Can't use 'super' outside of a class.")
        elif self.currentClass != ClassType.SUBCLASS:
            error_token(expr.keyword, "Can't user 'super' in a class with no superclass.")
        self.resolveLocal(expr, expr.keyword)
        return None
    
    def visitArray(self, expr):
        for element in expr.elements:
            self.resolve(element)
        return None