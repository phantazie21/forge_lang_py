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
from forge_native import nativeFunctions, nativeGlobals, ForgeNative
from forge_array import ForgeArray, ForgeIndexable
import math

def get_type(obj):
    if isinstance(obj, Literal):
        obj = obj.value
    if isinstance(obj, bool):
        return "boolean"
    elif isinstance(obj, float) or isinstance(obj, int):
        return "num"
    elif isinstance(obj, str):
        return "str"
    elif isinstance(obj, (ForgeFunction, ForgeNative)):
        return "function"
    elif isinstance(obj, ForgeClass):
        return "class"
    elif isinstance(obj, ForgeArray):
        return "array"
    elif isinstance(obj, ForgeInstance):
        return obj._class.name
    elif obj is None:
        return None

    return str(obj)

def get_value(obj):
    if obj == None:
        return None
    if isinstance(obj, Literal):
        obj = obj.value
    if get_type(obj) == "str":
        obj = f'"{obj}"'
    return obj

class Compiler:
    def __init__(self, tree):
        self.tree = tree
        self.functions = []
        self._else = []
        self._vars = {}
        self.code = ""

    def sort_tree(self):
        for node in self.tree:
            if isinstance(node, Function):
                self.functions.append(node)
            else:
                self._else.append(node)
        self.tree = self.functions + self._else

    def visitLiteral(self, literal):
        if isinstance(literal.value, str):
            return f'"{literal.value}"'
        else:
            return literal.value 
    
    def visitGrouping(self, grouping):
        return self.evaluate(grouping.expr_expression)

    def evaluate(self, expr):
        return expr.accept(self)

    def visitBinary(self, binary):
        left_type = type(binary.expr_left)
        right_type = type(binary.expr_right)
        left = self.evaluate(binary.expr_left)
        right = self.evaluate(binary.expr_right)
        try:
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
        except RuntimeException as e:
            runtimeError(e)

    def checkNumberOperands(self, operator, left, right):
        if isinstance(left, (int, float)) and isinstance(right, (int, float)):
            return
        raise RuntimeException(f"Operands must be numbers. Got {left} and {right}", operator)

    def isTruthy(self, obj):
        if obj == None:
            return False
        if isinstance(obj, str):
            return obj != ""
        if isinstance(obj, float):
            return obj != 0
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

    def visitVar(self, varStatement):
        value = None
        if varStatement.initializer != None:
            value = self.evaluate(varStatement.initializer)
            _type = get_type(value)
            print(_type)
            #if (_type == "str"):
                #value = f'"{value}"'
        self._vars[varStatement.name.lexeme] = value
        self.code += f"\tVar {varStatement.name.lexeme};\n"
        if (value != None):
            if value == True:
                value = "true"
            self.code += f"\t{varStatement.name.lexeme}.varion.{_type} = {value};\n"
            self.code += f"\t{varStatement.name.lexeme}.kind = {_type.upper()};\n"
        else:
            self.code += f"\t{varStatement.name.lexeme}.kind = NONE;\n"
        return None
    
    def visitVariable(self, varExpression):
        #print(self._vars)
        #return self._vars[varExpression.name.lexeme]
        #return f"{varExpression.name.lexeme}.{get_type(self._vars[varExpression.name.lexeme])}"
        return varExpression.name.lexeme

    def stringify(self, obj):
        if obj == None:
            return "null"
        if isinstance(obj, float):
            text = str(obj)
            if text.endswith(".0"):
                text = text[:-2]
            return f'"{text}"'
        if isinstance(obj, ForgeArray):
            text = "["
            for element in obj.elements:
                text += f"{element}, "
            text = text.rstrip(", ")
            text += "]"
            return text
        try:
            return obj.__str__()
        except:
            return str(obj)
    
    def visitPrint(self, printStatement):
        value = self.evaluate(printStatement.expr)
        if isinstance(printStatement.expr, Variable):
            self.code += f"\tprint_var({value});\n"
        else:
            self.code += f"\tprint({self.stringify(value)});\n"
        #print(self.stringify(value))
        return None

    def visitAssign(self, assignExpr):
        value = self.evaluate(assignExpr.value)
        
        distance = self.locals.get(assignExpr)
        if distance:
            self.environment.assignAt(distance, assignExpr.name, value)
        else:
            self.globals.assign(assignExpr.name, value)

        return value
    
    def generate(self, statement):
        if statement:
            statement.accept(self)

    def generate_code(self):
        self.sort_tree()
        self.code = '#include "base.h"\n'
        for fn in self.functions:
            self.code += str(fn) + "\n"
        self.code += 'int main(int argc, const char** argv) {\n'
        for _any in self._else:
            self.generate(_any)
            '''if isinstance(_any, Var):
                _type = get_type(_any.initializer)
                value = get_value(_any.initializer)
                code += f"\tunion var {_any.name.lexeme};\n"
                if (value != None):
                    if value == True:
                        value = "true"
                    code += f"\t{_any.name.lexeme}.{_type} = {value};\n"
                self._vars[_any.name.lexeme] = [_type, value]
            elif isinstance(_any, Print):
                _type = ""
                value = ""
                if isinstance(_any.expr, Literal):
                    _type = get_type(_any.expr)
                    value = get_value(_any.expr)
                else:
                    #print(self._vars[_any.expr.name.lexeme])
                    _type = self._vars[_any.expr.name.lexeme][0]
                    value = self._vars[_any.expr.name.lexeme][1]
                print(_type)
                if _type == "str":
                    code += f"\tprint({value});\n"
                if _type == "boolean":
                    code += f'\tprint("{value}");\n'
                elif _type == "num":
                    code += f"\tprint_num({value});\n"'''
        self.code += '\treturn 0;\n}'
        return self.code