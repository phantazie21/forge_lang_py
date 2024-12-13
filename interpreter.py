from forge_token import ForgeToken, TokenType
from error import *
from environment import Environment
from stmt import *
from expr import *

class BreakException(Exception):
    pass

class ContinueException(Exception):
    pass

class Interpreter:
    def __init__(self):
        self.environment = Environment()
        self.isInLoop = False

    def visitLiteral(self, literal):
        return literal.value
    
    def visitGrouping(self, grouping):
        return self.evaluate(grouping.expression)
    
    def evaluate(self, expr):
        return expr.accept(self)

    def visitBinary(self, binary):
        left = self.evaluate(binary.expr_left)
        right = self.evaluate(binary.expr_right)
        if binary.operator.tokenType == TokenType.PLUS:
            if isinstance(left, str) or isinstance(right, str):
                if isinstance(left, str) and isinstance(right, str):
                    return left + right
                if isinstance(left, float):
                    return self.stringify(left) + right
                if isinstance(right, float):
                    return left + self.stringify(right)

            self.checkNumberOperands(binary.operator, left, right)
            return left + right
        elif binary.operator.tokenType == TokenType.MINUS:
            self.checkNumberOperands(binary.operator, left, right)
            return left - right
        elif binary.operator.tokenType == TokenType.STAR:
            self.checkNumberOperands(binary.operator, left, right)
            return left * right
        elif binary.operator.tokenType == TokenType.SLASH:
            self.checkNumberOperands(binary.operator, left, right)
            return left / right
        elif binary.operator.tokenType == TokenType.GREATER:
            self.checkNumberOperands(binary.operator, left, right)
            return left > right
        elif binary.operator.tokenType == TokenType.GREATER_EQUAL:
            self.checkNumberOperands(binary.operator, left, right)
            return left >= right
        elif binary.operator.tokenType == TokenType.LESS:
            self.checkNumberOperands(binary.operator, left, right)
            return left < right
        elif binary.operator.tokenType == TokenType.LESS_EQUAL:
            self.checkNumberOperands(binary.operator, left, right)
            return left <= right
        elif binary.operator.tokenType == TokenType.EQUAL_EQUAL:
            return left == right
        elif binary.operator.tokenType == TokenType.BANG_EQUAL:
            return left != right
        return None

    def isTruthy(self, obj):
        if obj == None:
            return False
        if isinstance(obj, bool):
            return obj
        return True

    def visitUnary(self, unary):
        right = self.evaluate(unary.right)
        if unary.operator.tokenType == TokenType.MINUS:
            self.checkNumberOperand(unary.operator, right)
            return -right
        elif unary.operator.tokenType == TokenType.BANG:
            return not self.isTruthy(right)
        return None
    
    def visitVariable(self, varExpression):
        return self.environment.get(varExpression.name)
    
    def visitAssign(self, assignExpr):
        value = self.evaluate(assignExpr.value)
        self.environment.assign(assignExpr.name, value)
        return value
    
    def visitLogical(self, logicalExpr):
        left = self.evaluate(logicalExpr.left)

        if logicalExpr.operator.tokenType == TokenType.OR:
            if self.isTruthy(left):
                return left
        else:
            if not self.isTruthy(left):
                return left
            
        return self.evaluate(logicalExpr.right)
    
    def visitExpression(self, expressionStatement):
        self.evaluate(expressionStatement.expr)
        return None
    
    def visitPrint(self, printStatement):
        value = self.evaluate(printStatement.expr)
        print(self.stringify(value))
        return None
    
    def visitVar(self, varStatement):
        value = None
        if varStatement.initializer != None:
            value = self.evaluate(varStatement.initializer)
        self.environment.define(varStatement.name.lexeme, value)
        return None
    
    def visitBlock(self, blockStatement):
        self.executeBlock(blockStatement.statements, Environment(self.environment))
        return None
    
    def visitIf(self, ifStatement):
        if self.isTruthy(self.evaluate(ifStatement.condition)):
            self.execute(ifStatement.thenBranch)
                    
        elif ifStatement.elseBranch is not None:
            self.execute(ifStatement.elseBranch)
        return None
    
    def visitWhile(self, whileStatement):
        previousIsInLoop = self.isInLoop
        self.isInLoop = True
        try:
            while self.isTruthy(self.evaluate(whileStatement.condition)):
                try:
                    self.execute(whileStatement.body)
                except ContinueException:
                    if hasattr(whileStatement, 'increment'):
                        self.evaluate(whileStatement.increment)
                    continue
        except BreakException:
            pass
        finally:
            self.isInLoop = previousIsInLoop
        return None

    def visitBreak(self, breakStatement):
        if not self.isInLoop:
            raise RuntimeException("Break statement outside of loop.", breakStatement.token)
        raise BreakException()

    def visitContinue(self, continueStatement):
        if not self.isInLoop:
            raise RuntimeException("Continue statement outside of loop.", continueStatement.token)
        raise ContinueException()

    def executeBlock(self, statements, environment):
        previous = self.environment
        try:
            self.environment = environment
            for stmt in statements:
                self.execute(stmt)
        finally:
            self.environment = previous
    
    def checkNumberOperand(self, operator, operand):
        if isinstance(operand, int) or isinstance(operand, float):
            return
        raise RuntimeException(f"Operand must be a number. Got {operand}", operator)
    
    def checkNumberOperands(self, operator, left, right):
        if (isinstance(left, int) or isinstance(left, float)) and (isinstance(right, int) or isinstance(right, float)):
            return
        raise RuntimeException(f"Operands must be numbers. Got {left} and {right}", operator)
    
    def stringify(self, obj):
        if obj == None:
            return "nil"
        if isinstance(obj, float):
            text = str(obj)
            if text.endswith(".0"):
                text = text[:-2]
            return text
        return str(obj)

    def interpret(self, statements):
        try:
            for statement in statements:
                self.execute(statement)
        except RuntimeException as e:
            runtimeError(e)

    def execute(self, statement):
        if statement:
            statement.accept(self)