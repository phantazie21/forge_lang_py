from forge_callable import ForgeCallable
from forge_instance import ForgeInstance

class ForgeClass(ForgeCallable):
    def __init__(self, name, superclass, methods : dict):
        self.name = name
        self.superclass = superclass
        self.methods = methods

    def __str__(self):
        return self.name
    
    def call(self, interpreter, arguments):
        instance = ForgeInstance(self)
        initializer = self.findMethod("init")
        if initializer != None:
            initializer.bind(instance).call(interpreter, arguments)
        return instance
    
    def findMethod(self, name):
        if name in self.methods.keys():
            return self.methods.get(name)
        
        if self.superclass != None:
            return self.superclass.findMethod(name)

        return None
    
    def arity(self):
        initializer = self.findMethod("init")
        if initializer == None:
            return 0
        return initializer.arity()