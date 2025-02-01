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

class Compiler:
    def __init__(self, tree):
        self.tree = tree

    def generate_code(self):
        return self.tree