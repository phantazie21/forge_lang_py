from forge_callable import ForgeCallable
from forge_function import ForgeFunction
from forge_class import ForgeClass
from forge_instance import ForgeInstance
from error import FunctionException
import math

import time
from pathlib import Path

class ForgeNative(ForgeCallable):
    def __init__(self):
        self.name = None

    def arity(self):
        pass

    def call(self, interpreter, arguments):
        pass

    def __str__(self):
        return "<native fn>"
    
class Clock(ForgeNative):
    def __init__(self):
        self.name = "clock"

    def arity(self):
        return 0

    def call(self, interpreter, _):
        return time.time()
    
class Require(ForgeNative):
    def __init__(self):
        self.name = "require"

    def arity(self):
        return 1

    def call(self, interpreter, arguments):
        lib = arguments[0]
        lib_path = Path(str(lib))

        if lib_path.is_file() and lib_path.suffix == ".fl":
            '''sendRunFile(lib)'''
        else:
            raise FunctionException(f"{lib} not found or is not a valid ForgeLang library.", self.name)
        
class GetLine(ForgeNative):
    def __init__(self):
        self.name = "getline"

    def arity(self):
        return 0

    def call(self, interpreter, _):
        return input()
    
class Type(ForgeNative):
    def __init__(self):
        self.name = "type"

    def arity(self):
        return 1

    def call(self, interpreter, arguments):
        obj = arguments[0]

        if isinstance(obj, bool):
            return "boolean"
        elif isinstance(obj, float):
            return "number"
        elif isinstance(obj, str):
            return "string"
        elif isinstance(obj, (ForgeFunction, ForgeNative)):
            return "function"
        elif isinstance(obj, ForgeClass):
            return "class"
        elif isinstance(obj, ForgeInstance):
            return obj._class.name
        elif obj is None:
            return "null"

        return str(obj)
    
class ToString(ForgeNative):
    def __init__(self):
        self.name = "toString"

    def arity(self):
        return 1

    def call(self, interpreter, arguments):
        obj = arguments[0]

        if isinstance(obj, ForgeNative):
            return f"fn <{obj.name}>"

        return str(obj)

class ToNumber(ForgeNative):
    def __init__(self):
        self.name = "toNum"

    def arity(self):
        return 1

    def call(self, interpreter, arguments):
        obj = arguments[0]

        if not isinstance(obj, str):
            raise FunctionException("Expect type 'string'.", self.name)

        try:
            return float(obj)
        except ValueError:
            raise FunctionException("The string doesn't represent a valid number.", self.name)
        
class WriteToFile(ForgeNative):
    def __init__(self):
        self.name = "write"
    
    def arity(self):
        return 2
    
    def call(self, interpreter, arguments):
        lib = arguments[0]
        lib_path = Path(str(lib))

        if lib_path.is_file():
            try:
                with open(lib_path, "a") as f:
                    f.write(arguments[1])
            except Exception as e:
                raise FunctionException(e, self.name)
        else:
            raise FunctionException("The specified file cannot be found.", self.name)
        
class ClearFile(ForgeNative):
    def __init__(self):
        self.name = "clear"

    def arity(self):
        return 1
    
    def call(self, interpreter, arguments):
        lib = arguments[0]
        lib_path = Path(str(lib))

        try:
            open(lib_path, "w").close()
        except Exception as e:
            raise FunctionException(e, self.name)
        
class ReadFile(ForgeNative):
    def __init__(self):
        self.name = "read"

    def arity(self):
        return 1
    
    def call(self, interpreter, arguments):
        lib = arguments[0]
        lib_path = Path(str(lib))

        if lib_path.is_file():
            try:
                with open(lib_path, "r") as f:
                    return f.read()
            except Exception as e:
                raise FunctionException(e, self.name)
        else:
            raise FunctionException("The specified file cannot be found.", self.name)
        
class CreateFile(ForgeNative):
    def __init__(self):
        self.name = "create"

    def arity(self):
        return 1
    
    def call(self, interpreter, arguments):
        lib = arguments[0]
        lib_path = Path(str(lib))

        if not lib_path.is_file():
            try:
                open(lib_path, "w").close()
            except Exception as e:
                raise FunctionException(e, self.name)

class MathFunction(ForgeNative):
    def __init__(self):
        self.name = None

    def arity(self) -> int:
        return 1

    def check_number(self, argument):
        if not isinstance(argument, float):
            raise FunctionException("Expect type 'number'.", self.name)

        return argument

    def call(self, interpreter, arguments):
        pass

class Exponent(MathFunction):
    def __init__(self):
        self.name = "exp"

    def call(self, interpreter, arguments):
        obj = self.check_number(arguments[0])
        return math.exp(obj)
    
class Power(MathFunction):
    def __init__(self):
        self.name = "pow"

    def arity(self):
        return 2

    def call(self, interpreter, arguments):
        obj = self.check_number(arguments[0])
        obj2 = self.check_number(arguments[1])
        return math.pow(obj, obj2)

class Sqrt(MathFunction):
    def __init__(self):
        self.name = "sqrt"

    def call(self, interpreter, arguments):
        obj = self.check_number(arguments[0])
        return math.sqrt(obj)

class Log(MathFunction):
    def __init__(self):
        self.name = "log"
    
    def arity(self):
        return 2
    
    def call(self, interpreter, arguments):
        obj = self.check_number(arguments[0])
        obj2 = self.check_number(arguments[1])
        return math.log(obj2, obj)

class ToRadian(MathFunction):
    def __init__(self):
        self.name = "rad"

    def call(self, interpreter, arguments):
        obj = self.check_number(arguments[0])
        return math.radians(obj)
    
class Sin(MathFunction):
    def __init__(self):
        self.name = "sin"

    def call(self, interpreter, arguments):
        obj = self.check_number(arguments[0])
        return math.sin(obj)
    
class ArcSin(MathFunction):
    def __init__(self):
        self.name = "arcsin"

    def call(self, interpreter, arguments):
        obj = self.check_number(arguments[0])
        return math.asin(obj)
    
class Cos(MathFunction):
    def __init__(self):
        self.name = "cos"

    def call(self, interpreter, arguments):
        obj = self.check_number(arguments[0])
        return math.cos(obj)
    
class ArcCos(MathFunction):
    def __init__(self):
        self.name = "arccos"

    def call(self, interpreter, arguments):
        obj = self.check_number(arguments[0])
        return math.acos(obj)
    
class Tan(MathFunction):
    def __init__(self):
        self.name = "tan"

    def call(self, interpreter, arguments):
        obj = self.check_number(arguments[0])
        return math.tan(obj)
    
class ArcTan(MathFunction):
    def __init__(self):
        self.name = "arctan"

    def call(self, interpreter, arguments):
        obj = self.check_number(arguments[0])
        return math.atan(obj)
    
class Floor(MathFunction):
    def __init__(self):
        self.name = "floor"

    def call(self, interpreter, arguments):
        obj = self.check_number(arguments[0])
        return math.floor(obj)
    
class Ceiling(MathFunction):
    def __init__(self):
        self.name = "ceiling"

    def call(self, interpreter, arguments):
        obj = self.check_number(arguments[0])
        return math.ceil(obj)
    
class Round(MathFunction):
    def __init__(self):
        self.name = "round"

    def call(self, interpreter, arguments):
        obj = self.check_number(arguments[0])
        return round(obj)
    
class Absolute(MathFunction):
    def __init__(self):
        self.name = "abs"

    def call(self, interpreter, arguments):
        obj = self.check_number(arguments[0])
        return abs(obj)
    
class Sign(MathFunction):
    def __init__(self):
        self.name = "sign"

    def call(self, interpreter, arguments):
        obj = self.check_number(arguments[0])
        if obj > 0:
            return 1
        elif obj < 0:
            return -1
        return 0

nativeFunctions = [Clock, GetLine, Require, Type, ToString, ToNumber, Exponent, Power, Sqrt, Log, ToRadian, Sin, ArcSin, Cos, ArcCos, Tan, ArcTan, Floor, Ceiling, Round, Absolute, Sign, WriteToFile, ReadFile, ClearFile, CreateFile]
nativeGlobals = {"PI": math.pi, "E": math.e}