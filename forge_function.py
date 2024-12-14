from forge_callable import ForgeCallable
from environment import Environment
from forge_return import ReturnException

class ForgeFunction(ForgeCallable):
    def __init__(self, declaration, closure, isInitializer):
        self.declaration = declaration
        self.closure = closure
        self.isInitializer = isInitializer

    def call(self, interpreter, arguments):
        environment = Environment(self.closure)
        for i in range(len(self.declaration.params)):
            environment.define(self.declaration.params[i].lexeme, arguments[i])
        try:
            interpreter.executeBlock(self.declaration.body, environment)
        except ReturnException as e:
            if self.isInitializer:
                return self.closure.getAt(0, "this")
            return e.value
        
        if self.isInitializer:
            return self.closure.getAt(0, "this")

        return None
    
    def arity(self):
        return len(self.declaration.params)
    
    def __str__(self):
        return f"<fn {self.declaration.name.lexeme}>"
    
    def bind(self, instance):
        environment = Environment(self.closure)
        environment.define("this", instance)
        return ForgeFunction(self.declaration, environment, self.isInitializer)