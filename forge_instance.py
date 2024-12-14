from error import RuntimeException

class ForgeInstance:
    def __init__(self, _class):
        self._class = _class
        self.fields = {}

    def __str__(self):
        return self._class.name + " instance"
    
    def get(self, name):
        if name.lexeme in self.fields.keys():
            return self.fields.get(name.lexeme)
        
        method = self._class.findMethod(name.lexeme)
        if method != None:
            return method.bind(self)

        raise RuntimeException(f"Undefined property '{name.lexeme}'.", name)
    
    def set(self, name, value):
        self.fields |= {name.lexeme: value}