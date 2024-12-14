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
    
class Var(Stmt):
    def __init__(self, name, initializer):
        self.name = name
        self.initializer = initializer

    def accept(self, visitor):
        return visitor.visitVar(self)
    
    def __str__(self):
        return f"Var({self.name}, {self.initializer})"
    
class Block(Stmt):
    def __init__(self, statements):
        self.statements = statements
    
    def accept(self, visitor):
        return visitor.visitBlock(self)
    
    def __str__(self):
        return f"Block({self.statements})"
    
class If(Stmt):
    def __init__(self, condition, if_clause, else_clause=None):
        self.condition = condition
        self.thenBranch = if_clause
        self.elseBranch = else_clause

    def accept(self, visitor):
        return visitor.visitIf(self)
    
    def __str__(self):
        return f"If({self.condition}, {self.thenBranch}, {self.elseBranch})"
    
class While(Stmt):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

    def accept(self, visitor):
        return visitor.visitWhile(self)
    
    def __str__(self):
        return f"While({self.condition}, {self.body})"

class Break(Stmt):
    def __init__(self, token):
        self.token = token

    def accept(self, visitor):
        return visitor.visitBreak(self)
    
    def __str__(self):
        return f"Break({self.token})"

class Continue(Stmt):
    def __init__(self, token):
        self.token = token

    def accept(self, visitor):
        return visitor.visitContinue(self)
    
    def __str__(self):
        return f"Continue({self.token})"
    
class Function(Stmt):
    def __init__(self, name, params, body):
        self.name = name
        self.params = params
        self.body = body

    def accept(self, visitor):
        return visitor.visitFunction(self)
    
    def __str__(self):
        return f"Function({self.name}, {self.params}, {self.body})"
    
class Return(Stmt):
    def __init__(self, keyword, value):
        self.keyword = keyword
        self.value = value

    def accept(self, visitor):
        return visitor.visitReturn(self)
    
    def __str__(self):
        return f"Return({self.keyword}, {self.value})"
    
class Class(Stmt):
    def __init__(self, name, superclass, methods):
        self.name = name
        self.superclass = superclass
        self.methods = methods

    def accept(self, visitor):
        return visitor.visitClass(self)
    
    def __str__(self):
        return f"Class({self.name}, {self.superclass}, {self.methods})"