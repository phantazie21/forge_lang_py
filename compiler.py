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

    def sort_tree(self):
        for node in self.tree:
            if isinstance(node, Function):
                self.functions.append(node)
            else:
                self._else.append(node)
        self.tree = self.functions + self._else

    def generate_code(self):
        self.sort_tree()
        code = '#include "base.h"\n'
        for fn in self.functions:
            code += str(fn) + "\n"
        code += 'int main(int argc, const char** argv) {\n'
        for _any in self._else:
            if isinstance(_any, Var):
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
                    code += f"\tprint_num({value});\n"
        code += '\treturn 0;\n}'
        return code