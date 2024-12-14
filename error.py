from forge_token import TokenType

hadError = False
hadRuntimeError = False

class RuntimeException(Exception):
    def __init__(self, message, token):
        self.message = message
        self.token = token
        super().__init__(self.message)

class FunctionException(Exception):
    def __init__(self, message, function):
        self.function = function
        self.message = message
        super().__init__()

def error(line, message):
    report(line, message, "")

def error_token(token, message):
    if token.tokenType == TokenType.EOF:
        report(token.line , message, " at end")
        raise Exception()
    else:
        report(token.line, message, f" at '{token.lexeme}' ")
        raise Exception()

def runtimeError(error):
    global hadRuntimeError
    print(f"[line {error.token.line}] RuntimeError: {error.message}")
    hadRuntimeError = True

def report(line, message, where=None):
    global hadError
    print(f"[line {line}] Error{where}: {message}")
    hadError = True