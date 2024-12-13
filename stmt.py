class Stmt:
    pass

class Expression(Stmt):
    def __init__(self, expr):
        self.expr = expr

    def accept(self, visitor):
        return visitor.visitExpression(self)
    
    def __str__(self):
        return f"Expression({self.expr})"
    
class Print(Stmt):
    def __init__(self, expr):
        self.expr = expr

    def accept(self, visitor):
        return visitor.visitPrint(self)
    
    def __str__(self):
        return f"Print({self.expr})"