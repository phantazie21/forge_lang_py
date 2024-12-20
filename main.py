import sys
import forge_scanner

import forge_parser
from interpreter import Interpreter
from resolver import Resolver
from preprocessor import PreProcessor
import error

interpreter = Interpreter()
resolver = Resolver(interpreter)

def run(source, filename=""):
    global interpreter
    preprocessor = PreProcessor(source, filename)
    if error.hadError:
        return
    startLines = 1
    if len(preprocessor.includes) > 0:
        startLines = -preprocessor.lines + len(preprocessor.includes)
    scanner = forge_scanner.ForgeScanner(preprocessor.source, startLines)
    tokens = scanner.scanTokens()
    parser = forge_parser.Parser(tokens)
    expr = parser.parse()
    if error.hadError:
        return

    resolver.resolveStatements(expr)
    interpreter.interpret(expr)

def runPrompt():
    while True:
        prompt = input("> ")
        if (prompt == ""):
            break
        run(prompt)
        error.hadError = False

def runFile(filename):
    run(open(filename).read(), filename)
    if error.hadError:
        sys.exit(65)
    if error.hadRuntimeError:
        sys.exit(70)

def main():
    if len(sys.argv) > 2:
        print("Usage: python main.py <filename>")
        sys.exit(1)
    if len(sys.argv) == 2:
        filename = sys.argv[1]
        runFile(filename)
    else:
        runPrompt()

if __name__ == "__main__":
    main()