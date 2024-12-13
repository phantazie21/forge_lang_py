class Expr:
    pass

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