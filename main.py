import sys
import forge_scanner

import forge_parser
from interpreter import Interpreter
from resolver import Resolver

interpreter = Interpreter()
resolver = Resolver(interpreter)

def run(source):
    global interpreter
    scanner = forge_scanner.ForgeScanner(source)
    tokens = scanner.scanTokens()
    parser = forge_parser.Parser(tokens)
    expr = parser.parse()
    from error import hadError
    if hadError:
        sys.exit(65)

    resolver.resolveStatements(expr)
    interpreter.interpret(expr)

def runPrompt():
    while True:
        prompt = input("> ")
        if (prompt == ""):
            break
        run(prompt)
        hadError = False

def runFile(filename):
    run(open(filename).read())
    from error import hadRuntimeError
    if hadRuntimeError:
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

main()