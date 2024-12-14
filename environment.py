from error import *

class Environment:
    def __init__(self, enclosing=None):
        self.values = {}
        self.enclosing = enclosing

    def define(self, name, value):
        self.values |= {name: value}

    def get(self, name):
        if name.lexeme in self.values:
            return self.values[name.lexeme]

        if self.enclosing is not None:
            return self.enclosing.get(name)

        raise RuntimeException(f"Undefined variable '{name.lexeme}'.", name)
    
    def getAt(self, distance, name):
        return self.ancestor(distance).values.get(name)
    
    def ancestor(self, distance):
        environment = self
        for i in range(distance):
            environment = environment.enclosing

        return environment
    
    def assign(self, name, value):
        if name.lexeme in self.values:
            self.values[name.lexeme] = value
            return
        
        if self.enclosing is not None:
            self.enclosing.assign(name, value)
            return
        
        raise RuntimeException(f"Undefined variable '{name.lexeme}'", name)
    
    def assignAt(self, distance, name, value):
        self.ancestor(distance).values |= {name.lexeme: value}