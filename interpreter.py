from forge_token import ForgeToken, TokenType
from error import *

class Interpreter:
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
            if isinstance(left, str) and isinstance(right, str):
                return left + right
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

    def interpret(self, expr):
        try:
            value = self.evaluate(expr)
            print(self.stringify(value))
        except RuntimeException as e:
            runtimeError(e)