class Expr:
    pass

class Assign(Expr):
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def accept(self, visitor):
        return visitor.visitAssign(self)
    
    def __str__(self):
        return f"Assign({self.name}, {self.value})"

class Binary(Expr):
    def __init__(self, expr_left, token_operator, expr_right):
        self.expr_left = expr_left
        self.operator = token_operator
        self.expr_right = expr_right

    def accept(self, visitor):
        return visitor.visitBinary(self)
    
    def __str__(self):
        return f"Binary({self.expr_left}, {self.operator}, {self.expr_right})"

class Grouping(Expr):
    def __init__(self, expr_expression):
        self.expr_expression = expr_expression

    def accept(self, visitor):
        return visitor.visitGrouping(self)

    def __str__(self):
        return f"Grouping({self.expr_expression})"
    
class Literal(Expr):
    def __init__(self, object_value):
        self.value = object_value

    def accept(self, visitor):
        return visitor.visitLiteral(self)

    def __str__(self):
        return f"Literal({self.value})"

class Unary(Expr):
    def __init__(self, token_operator, expr_right):
        self.token_operator = token_operator
        self.expr_right = expr_right

    def accept(self, visitor):
        return visitor.visitUnary(self)

    def __str__(self):
        return f"Unary({self.token_operator}, {self.expr_right})"
    
class Logical(Expr):
    def __init__(self, expr_left, operator, expr_right):
        self.left = expr_left
        self.operator = operator
        self.right = expr_right

    def accept(self, visitor):
        return visitor.visitLogical(self)
    
    def __str__(self):
        return f"Logical({self.expr_left}, {self.operator}, {self.expr_right})"

class Variable(Expr):
    def __init__(self, token_name):
        self.name = token_name

    def accept(self, visitor):
        return visitor.visitVariable(self)

    def __str__(self):
        return f"Variable({self.name})"
    
class Call(Expr):
    def __init__(self, callee, paren, args):
        self.callee = callee
        self.paren = paren
        self.args = args
    
    def accept(self, visitor):
        return visitor.visitCall(self)
    
    def __str__(self):
        return f"Call({self.callee}, {self.paren}, {self.args})"
    
class Get(Expr):
    def __init__(self, _object, name):
        self.object = _object
        self.name = name

    def accept(self, visitor):
        return visitor.visitGet(self)
    
    def __str__(self):
        return f"Get({self.object}, {self.name})"
    
class Set(Expr):
    def __init__(self, _object, name, value):
        self.object = _object
        self.name = name
        self.value = value

    def accept(self, visitor):
        return visitor.visitSet(self)
    
    def __str__(self):
        return f"Set({self.object}, {self.name}, {self.value})"
    
class This(Expr):
    def __init__(self, keyword):
        self.keyword = keyword

    def accept(self, visitor):
        return visitor.visitThis(self)
    
    def __str__(self):
        return f"This({self.keyword})"
    
class Super(Expr):
    def __init__(self, keyword, method):
        self.keyword = keyword
        self.method = method

    def accept(self, visitor):
        return visitor.visitSuper(self)

    def __str__(self):
        return f"Super({self.keyword}, {self.method})"