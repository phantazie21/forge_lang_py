hadError = False
hadRuntimeError = False

class RuntimeException(Exception):
    def __init__(self, message, token):
        super().__init__(message)
        self.message = message
        self.token = token

def error(line, message):
    report(line, message, "")

def runtimeError(error):
    global hadRuntimeError
    print(f"[line {error.token.line}] RuntimeError: {error.message}")
    hadRuntimeError = True

def report(line, message, where=None):
    global hadError
    print(f"[line {line}] Error{where}: {message}")
    hadError = True