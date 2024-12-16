from forge_callable import ForgeCallable
import math
from error import NativeException, RuntimeException
from forge_indexable import ForgeIndexable

class Add(ForgeCallable):
    def __init__(self, array):
        self.array = array

    def arity(self):
        return 0
    
    def variadic(self):
        return True
    
    def call(self, interpreter, arguments):
        self.array.elements.extend(arguments)
        
class Remove(ForgeCallable):
    def __init__(self, array):
        self.array = array

    def arity(self):
        return 1
    
    def call(self, interpreter, arguments):
        try:
            return self.array.elements.pop(0)
        except Exception as e:
            raise NativeException("Array is empty.", "remove")
        
class RemoveAt(ForgeCallable):
    def __init__(self, array):
        self.array = array

    def arity(self):
        return 1
    
    def call(self, interpreter, arguments):
        try:
            if len(self.array.elements) == 0:
                raise Exception("Array is empty.")
            if not isinstance(arguments[0], float):
                raise TypeError()
            arguments[0] = math.floor(arguments[0])
            if arguments[0] >= len(self.array.elements):
                raise IndexError()
            del self.array.elements[arguments[0]]
            return None
        except TypeError:
            raise NativeException("Index must be a number.", "removeAt")
        except IndexError:
            raise NativeException("Index out of range.", "removeAt")
        except Exception as e:
            raise NativeException(e, "removeAt")
        
class RemoveValue(ForgeCallable):
    def __init__(self, array):
        self.array = array

    def arity(self):
        return 1
    
    def call(self, interpreter, arguments):
        try:
            if len(self.array.elements) == 0:
                raise Exception("Array is empty.")
            return self.array.elements.remove(arguments[0])
        except Exception as e:
            raise NativeException(e, "removeAt")
        
class Push(ForgeCallable):
    def __init__(self, array):
        self.array = array

    def arity(self):
        return 1
    
    def call(self, interpreter, arguments):
        try:
            return self.array.elements.insert(0, arguments[0])
        except Exception as e:
            raise NativeException("Error while pushing." "push")

class Pop(ForgeCallable):
    def __init__(self, array):
        self.array = array

    def arity(self):
        return 0
    
    def call(self, interpreter, arguments):
        try:
            return self.array.elements.pop()
        except Exception as e:
            raise NativeException("Array is empty.", "pop")
        
class Length(ForgeCallable):
    def __init__(self, array):
        self.array = array

    def arity(self):
        return 0
    
    def call(self, interpreter, arguments):
        return len(self.array.elements)
    
class IsEmpty(ForgeCallable):
    def __init__(self, array):
        self.array = array

    def arity(self):
        return 0
    
    def call(self, interpreter, arguments):
        return len(self.array.elements) == 0
    
class Contains(ForgeCallable):
    def __init__(self, array):
        self.array = array

    def arity(self):
        return 1
    
    def call(self, interpreter, arguments):
        return arguments[0] in self.array.elements
    
class Clear(ForgeCallable):
    def __init__(self, array):
        self.array = array

    def arity(self):
        return 0
    
    def call(self, interpreter, arguments):
        self.array.elements = []
        return None

class ForgeArray(ForgeIndexable):
    def __init__(self, elements):
        self.elements = elements
        self.methods = self.createMethods()

    def createMethods(self):
        methods = {}
        methods |= {"add": Add(self)}
        methods |= {"remove": Remove(self)}
        methods |= {"push": Push(self)}
        methods |= {"pop": Pop(self)}
        methods |= {"length": Length(self)}
        methods |= {"contains": Contains(self)}
        methods |= {"clear": Clear(self)}
        methods |= {"removeAt": RemoveAt(self)}
        methods |= {"removeValue": RemoveValue(self)}
        return methods

    def getMethod(self, name):
        if name.lexeme in self.methods.keys():
            return self.methods.get(name.lexeme)
        else:
            raise RuntimeException("No such method.", name)

    def get(self, token, index):
        idx = self.indexToInteger(token, index)
        try:
            return self.elements[idx]
        except Exception as e:
            raise RuntimeException("Index out of range.", token)
        
    def _set(self, token, index, item):
        idx = self.indexToInteger(token, index)
        try:
            self.elements[idx] = item
        except Exception as e:
            raise RuntimeException("Index out of range.", token)
        
    def length(self):
        return len(self.elements)

    def indexToInteger(self, token, index):
        if isinstance(index, float):
            return math.floor(index)
        else:
            raise RuntimeException("Index must be a number.", token)