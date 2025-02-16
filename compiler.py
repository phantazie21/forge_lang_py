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

ARG_COUNT = 1

def get_type(obj):
    if isinstance(obj, Literal):
        obj = obj.value
    if isinstance(obj, bool) or obj == "false" or obj == "true":
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
        self.varexprs = []
        self._else = []
        self._vars = {}
        self.code = ""
        self.main_code = ""

    def sort_tree(self):
        for node in self.tree:
            if isinstance(node, Function):
                self.functions.append(node)
            elif isinstance(node, Var):
                self.varexprs.append(node)
            else:
                self._else.append(node)
        self.tree = self.varexprs + self.functions + self._else

    def visitLiteral(self, literal):
        if isinstance(literal.value, str):
            return f'"{literal.value}"'
        elif isinstance(literal.value, bool):
            return str(literal.value).lower()
        else:
            return literal.value 

    def visitExpression(self, expressionStatement):
        self.evaluate(expressionStatement.expr)
        return None
    
    def visitGrouping(self, grouping):
        if isinstance(grouping.expr_expression, Logical):
            self.code += "("
            self.evaluate(grouping.expr_expression)
            self.code += ")"
            return
        return self.evaluate(grouping.expr_expression)

    def evaluate(self, expr):
        return expr.accept(self)

    def visitFunction(self, functionStatement):
        #function = ForgeFunction(functionStatement, None, False)
        self.code += f"Var {functionStatement.name.lexeme}("
        for i in range(len(functionStatement.params)):
            self.code += f"Var {functionStatement.params[i].lexeme}"
            if i < len(functionStatement.params) - 1:
                self.code += ", "
        self.code += ") {\n"
        self.code += "\tVar _return;\n\t_return.kind = NONE;\n"
        try:
            self.executeBlock(functionStatement.body)
            self.code += "\treturn _return;\n";
            self.code += "}\n"
        except ReturnException:
            return
        #self.environment.define(functionStatement.name.lexeme, function)

    def visitReturn(self, returnStatement):
        if returnStatement.value == None:
            return
        if isinstance(returnStatement.value, Variable):
            self.code += f"\t_return.varion = {returnStatement.value.name.lexeme}.varion;\n"
            self.code += "\treturn _return;\n"
            self.code += "}\n"
            raise ReturnException(None)
        else:
            value = self.evaluate(returnStatement.value)
            if value:
                self.code += f"\t_return.varion.{get_type(value)} = {value};\n"
                self.code += f"\t_return.kind = {get_type(value).upper()};\n"

    def visitCall(self, callExpr):
        global ARG_COUNT
        passed_args = []
        for arg in callExpr.args:
            if isinstance(arg, Variable):
                passed_args.append(arg.name.lexeme)
            else:
                self.code += f"\tVar arg{ARG_COUNT};\n"
                value = self.evaluate(arg)
                self.code += f"\targ{ARG_COUNT}.varion.{get_type(value)} = {value};\n"
                self.code += f"\targ{ARG_COUNT}.kind = {get_type(value).upper()};\n"
                passed_args.append(f"arg{ARG_COUNT}")
                ARG_COUNT += 1
        self.code += f"\t{callExpr.callee.name.lexeme}("
        for i in range(len(callExpr.args)):
            self.code += str(passed_args[i])
            if i < len(callExpr.args) - 1:
                self.code += ", "
        self.code += ");\n"

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
                    if not (left.endswith('"') and left.startswith('"')):
                        if left in self._vars.keys():
                            left = self._vars[left]
                            #print(left)
                            if isinstance(left, str):
                                return left * math.floor(right)
                        else:
                            raise RuntimeException(f"{left} is not a valid variable, string or number", binary.operator)
                    else:
                        return left * math.floor(right)
                if isinstance(left, float) and isinstance(right, str):
                    if not (right.endswith('"') and right.startswith('"')):
                        if right in self._vars.keys():
                            right = self._vars[right]
                            #print(right)
                            if isinstance(right, str):
                                return math.floor(left) * right
                        else:
                            raise RuntimeException(f"{right} is not a valid variable, string or number", binary.operator)
                    else:
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
                return f"{left} > {right}"
            elif binary.operator.tokenType == TokenType.GREATER_EQUAL:
                self.checkNumberOperands(binary.operator, left, right)
                return f"{left} >= {right}"
            elif binary.operator.tokenType == TokenType.LESS:
                return f"{left} < {right}"
            elif binary.operator.tokenType == TokenType.LESS_EQUAL:
                self.checkNumberOperands(binary.operator, left, right)
                return f"{left} <= {right}"
            elif binary.operator.tokenType == TokenType.EQUAL_EQUAL:
                if (left in self._vars):
                    left = f"{left}.varion.{get_type(self._vars[left])}"
                return f"{left} == {right}"
            elif binary.operator.tokenType == TokenType.BANG_EQUAL:
                return f"{left} != {right}"
            return None
        except RuntimeException as e:
            runtimeError(e)

    def checkNumberOperand(self, operator, operand):
        if isinstance(operand, int) or isinstance(operand, float):
            return
        raise RuntimeException(f"Operand must be a number. Got {operand}", operator)

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
        _type = None
        isVar = False
        varName = ""
        if varStatement.name.lexeme in self._vars.keys():
            return
        if varStatement.initializer != None:
            value = self.evaluate(varStatement.initializer)
            _type = get_type(value)
            if value in self._vars.keys():
                isVar = True
                varName = value
                value = self._vars[value]
        self._vars[varStatement.name.lexeme] = value
        self.code += f"Var {varStatement.name.lexeme};\n"
        if varStatement not in self.varexprs:
            if (value != None):
                '''if value == True or value == False:
                    value = str(value).lower()'''
                if isVar:
                    self.code += f"\t{varStatement.name.lexeme}.varion = {varName}.varion;\n"
                    self.code += f"\t{varStatement.name.lexeme}.kind = {varName}.kind;\n"
                else:
                    self.code += f"\t{varStatement.name.lexeme}.varion.{_type} = {value};\n"
                    self.code += f"\t{varStatement.name.lexeme}.kind = {_type.upper()};\n"
            else:
                self.code += f"\t{varStatement.name.lexeme}.kind = NONE;\n"
        else:
            if (value != None):
                '''if value == True or value == False:
                    value = str(value).lower()'''
                if isVar:
                    self.main_code += f"\t{varStatement.name.lexeme}.varion = {varName}.varion;\n"
                    self.main_code += f"\t{varStatement.name.lexeme}.kind = {varName}.kind;\n"
                else:
                    self.main_code += f"\t{varStatement.name.lexeme}.varion.{_type} = {value};\n"
                    self.main_code += f"\t{varStatement.name.lexeme}.kind = {_type.upper()};\n"
            else:
                self.main_code += f"\t{varStatement.name.lexeme}.kind = NONE;\n"
        return None
    
    def visitVariable(self, varExpression):
        return varExpression.name.lexeme

    def visitLogical(self, logicalExpr):
        if isinstance(logicalExpr.left, Variable):
            self.code += f"{logicalExpr.left.name.lexeme}.varion.{get_type(self._vars[logicalExpr.left.name.lexeme])}"
        else:
            self.generate(logicalExpr.left)

        if logicalExpr.operator.tokenType == TokenType.OR:
            self.code += " || "
        else:
            self.code += " && "

        if isinstance(logicalExpr.right, Variable):
            self.code += f"{logicalExpr.right.name.lexeme}.varion.{get_type(self._vars[logicalExpr.right.name.lexeme])}"
        else:
            self.generate(logicalExpr.right)
        '''if logicalExpr.operator.tokenType == TokenType.OR:
            if self.isTruthy(left):
                return left
        else:
            if not self.isTruthy(left):
                return left
            
        return self.evaluate(logicalExpr.right)'''
    
    def visitWhile(self, whileStatement):
        self.code += f"\twhile ("
        cond = self.evaluate(whileStatement.condition)
        if cond:
            self.code += cond
        self.code += ") {\n\t"
        self.generate(whileStatement.body)
        self.code += "\t}\n"

    def visitBlock(self, blockStatement):
        self.executeBlock(blockStatement.statements)
        return None

    def executeBlock(self, statements):
        for stmt in statements:
            self.generate(stmt)

    def visitIf(self, ifStatement):
        '''if self.isTruthy(self.evaluate(ifStatement.condition)):
            self.execute(ifStatement.thenBranch)
                    
        elif ifStatement.elseBranch is not None:
            self.execute(ifStatement.elseBranch)'''
        #print(ifStatement.condition)
        self.code += "\tif ("
        if isinstance(ifStatement.condition, Variable):
            self.code += f"{ifStatement.condition.name.lexeme}.varion.{get_type(self._vars[ifStatement.condition.name.lexeme])}"
        else:
            cond = self.evaluate(ifStatement.condition)
            if cond:
                self.code += cond
        self.code += ") {\n\t"
        self.generate(ifStatement.thenBranch)  # Properly generate the block
        self.code += "\t}\n"

        if ifStatement.elseBranch is not None:
            if isinstance(ifStatement.elseBranch, If):
                self.code += "\telse"
            else:
                self.code += "\telse {\n\t"
            self.generate(ifStatement.elseBranch)  # Generate the else block
            if not isinstance(ifStatement.elseBranch, If):
                self.code += "\t}\n"
        return None

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
        #print(self.code)
        if isinstance(printStatement.expr, Variable):
            self.code += f"\tprint_var({value});\n"
        else:
            self.code += f"\tprint({self.stringify(value)});\n"
        #print(self.code)
        #print(self.stringify(value))
        return None

    def visitAssign(self, assignExpr):
        if isinstance(assignExpr.value, Variable):
            self.code += f"\t{assignExpr.name.lexeme}.varion = {assignExpr.value.name.lexeme}.varion;\n"
            self.code += f"\t{assignExpr.name.lexeme}.kind = {assignExpr.value.name.lexeme}.kind;\n"
        else:
            value = self.evaluate(assignExpr.value)
            _type = get_type(value)
            self.code += f"\t{assignExpr.name.lexeme}.varion.{_type} = {value};\n"
            self.code += f"\t{assignExpr.name.lexeme}.kind = {_type.upper()};\n"
            self._vars[assignExpr.name.lexeme] = value
    
    def generate(self, statement):
        if statement:
            statement.accept(self)

    def generate_code(self):
        try:
            self.sort_tree()
            self.code = '#include "base.h"\n'
            for _var in self.varexprs:
                self.generate(_var)
            for fn in self.functions:
                self.generate(fn)
            self.code += 'int main(int argc, const char** argv) {\n'
            self.code += self.main_code
            for _any in self._else:
                self.generate(_any)
            self.code += '\treturn 0;\n}'
            return self.code
        except RuntimeException as e:
            runtimeError(e)
