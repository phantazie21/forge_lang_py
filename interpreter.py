from forge_token import TokenType
from error import *
from environment import Environment
from stmt import *
from expr import *
from forge_callable import ForgeCallable
from forge_function import ForgeFunction
from forge_return import ReturnException
from forge_class import ForgeClass
from forge_instance import ForgeInstance
from forge_native import nativeFunctions, nativeGlobals
from forge_array import ForgeArray, ForgeIndexable
import math

class BreakException(Exception):
    pass

class ContinueException(Exception):
    pass

class Interpreter:
    def __init__(self):
        self.globals = Environment()
        self.environment = self.globals
        self.isInLoop = False
        self.locals = {}
        self.defineNatives(nativeFunctions)
        self.defineGlobals(nativeGlobals)

    def defineNatives(self, functions):
        for native in functions:
            native = native()
            self.globals.define(native.name, native)

    def defineGlobals(self, constants):
        for name, value in constants.items():
            self.globals.define(name, value)

    def visitLiteral(self, literal):
        return literal.value
    
    def visitGrouping(self, grouping):
        return self.evaluate(grouping.expr_expression)
    
    def evaluate(self, expr):
        return expr.accept(self)

    def visitBinary(self, binary):
        left = self.evaluate(binary.expr_left)
        right = self.evaluate(binary.expr_right)
        if binary.operator.tokenType == TokenType.PLUS:
            if isinstance(left, str) or isinstance(right, str):
                if isinstance(left, str) and isinstance(right, str):
                    return left + right
                if isinstance(right, str):
                    return self.stringify(left) + right
                if isinstance(left, str):
                    return left + self.stringify(right)

            self.checkNumberOperands(binary.operator, left, right)
            return left + right
        elif binary.operator.tokenType == TokenType.MINUS:
            self.checkNumberOperands(binary.operator, left, right)
            return left - right
        elif binary.operator.tokenType == TokenType.STAR:
            if isinstance(left, str) and isinstance(right, float):
                return left * math.floor(right)
            if isinstance(left, float) and isinstance(right, str):
                return math.floor(left) * right
            if isinstance(left, ForgeArray) and isinstance(right, float):
                return ForgeArray(left.elements * math.floor(right))
            if isinstance(left, float) and isinstance(right, ForgeArray):
                return ForgeArray(right.elements * math.floor(left))
            self.checkNumberOperands(binary.operator, left, right)
            return left * right
        elif binary.operator.tokenType == TokenType.SLASH:
            self.checkNumberOperands(binary.operator, left, right)
            return left / right
        elif binary.operator.tokenType == TokenType.MODULO:
            self.checkNumberOperands(binary.operator, left, right)
            return left % right
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
        right = self.evaluate(unary.expr_right)
        if unary.token_operator.tokenType == TokenType.MINUS:
            self.checkNumberOperand(unary.token_operator, right)
            return -right
        elif unary.token_operator.tokenType == TokenType.BANG:
            return not self.isTruthy(right)
        return None
    
    def visitVariable(self, varExpression):
        return self.lookUpVariable(varExpression.name, varExpression)
    
    def lookUpVariable(self, name, expr):
        distance = self.locals.get(expr)
        if distance is not None:
            return self.environment.getAt(distance, name.lexeme)
        else:
            return self.globals.get(name)

    def visitAssign(self, assignExpr):
        value = self.evaluate(assignExpr.value)
        
        distance = self.locals.get(assignExpr)
        if distance:
            self.environment.assignAt(distance, assignExpr.name, value)
        else:
            self.globals.assign(assignExpr.name, value)

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

    def visitCall(self, callExpr):
        callee = self.evaluate(callExpr.callee)

        arguments = []
        for argument in callExpr.args:
            arguments.append(self.evaluate(argument))
        
        if not isinstance(callee, ForgeCallable):
            raise RuntimeException("Can only call functions and classes.", callExpr.paren)
        
        function = callee

        if len(arguments) != function.arity() and not function.variadic():
            raise RuntimeException(f"Expected {function.arity()} arguments, but got {len(arguments)}.", callExpr.paren)
        try:
            return function.call(self, arguments)
        except FunctionException as e:
            raise RuntimeException(f"in function {e.function}: {e.message}", callExpr.paren)
        except NativeException as e:
            raise RuntimeException(f"in function {e.function}: {e.message}", callExpr.paren)
    
    def visitGet(self, expr):
        _object = self.evaluate(expr.object)
        if isinstance(_object, ForgeInstance):
            return _object.get(expr.name)
        if isinstance(_object, ForgeArray):
            return _object.getMethod(expr.name)
        raise RuntimeException("Only instances have properties.", expr.name)
    
    def visitSet(self, expr):
        _object = self.evaluate(expr.object)
        if not isinstance(_object, ForgeInstance):
            raise RuntimeException("Only instances have fields.", expr.name)
        value = self.evaluate(expr.value)
        _object.set(expr.name, value)
        return value
    
    def visitThis(self, expr):
        return self.lookUpVariable(expr.keyword, expr)
    
    def visitArray(self, expr):
        elements = [self.evaluate(element) for element in expr.elements]
        return ForgeArray(elements)

    def visitExpression(self, expressionStatement):
        self.evaluate(expressionStatement.expr)
        return None
    
    def visitFunction(self, functionStatement):
        function = ForgeFunction(functionStatement, self.environment, False)
        self.environment.define(functionStatement.name.lexeme, function)
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
                        self.executeWithEnvironment(whileStatement.increment, Environment(self.environment))
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
    
    def visitReturn(self, returnStatement):
        value = None
        if returnStatement.value != None:
            value = self.evaluate(returnStatement.value)
        
        raise ReturnException(value)
    
    def visitClass(self, stmt):
        superclass = None
        if stmt.superclass != None:
            superclass = self.evaluate(stmt.superclass)
            if not isinstance(superclass, ForgeClass):
                raise RuntimeException("Superclass must be a class.", stmt.superclass.name)
        self.environment.define(stmt.name.lexeme, None)

        if stmt.superclass is not None:
            self.environment = Environment(self.environment)
            self.environment.define("super", superclass)

        methods = {}
        for method in stmt.methods:
            function = ForgeFunction(method, self.environment, method.name.lexeme == "init")
            methods[method.name.lexeme] = function
        _class = ForgeClass(stmt.name.lexeme, superclass, methods)

        if superclass is not None:
            self.environment = self.environment.enclosing

        self.environment.assign(stmt.name, _class)
        return None
    
    def visitSuper(self, expr):
        distance = self.locals.get(expr)
        superclass = self.environment.getAt(distance, "super")

        _object = self.environment.getAt(distance - 1, "this")

        method = superclass.findMethod(expr.method.lexeme)

        if method is None:
            raise RuntimeException(f"Undefined property '{expr.method.lexeme}'.", expr.method)

        return method.bind(_object)

    def visitIndexGet(self, expr):
        indexee = self.evaluate(expr.indexee)
        index = self.evaluate(expr.index)
        if isinstance(indexee, ForgeIndexable):
            return indexee.get(expr.bracket, index)
        else:
            raise RuntimeException("Variable must be indexable.", expr.bracket)
    
    def visitIndexSet(self, expr):
        indexee = self.evaluate(expr.indexee)
        if not isinstance(indexee, ForgeIndexable):
            raise RuntimeException("Variable must be indexable.", expr.bracket)
        
        index = self.evaluate(expr.index)
        value = self.evaluate(expr.value)
        indexee._set(expr.bracket, index, value)
        return value

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
        if isinstance(left, (int, float)) and isinstance(right, (int, float)):
            return
        raise RuntimeException(f"Operands must be numbers. Got {left} and {right}", operator)
    
    def stringify(self, obj):
        if obj == None:
            return "null"
        if isinstance(obj, float):
            text = str(obj)
            if text.endswith(".0"):
                text = text[:-2]
            return text
        if isinstance(obj, ForgeArray):
            text = "["
            for element in obj.elements:
                text += f"{element}, "
            text = text.rstrip(", ")
            text += "]"
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

    def executeWithEnvironment(self, statement, environment):
        previous = self.environment
        try:
            self.environment = environment
            self.execute(statement)
        finally:
            self.environment = previous

    def resolve(self, expr, depth):
        self.locals[expr] = depth