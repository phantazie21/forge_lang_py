import sys
import forge_scanner
from error import *
import forge_parser
from interpreter import Interpreter

interpreter = Interpreter()

def run(source):
    global interpreter
    global hadError
    global hadRuntimeError
    scanner = forge_scanner.ForgeScanner(source)
    tokens = scanner.scanTokens()
    parser = forge_parser.Parser(tokens)
    expr = parser.parse()
    if hadError:
        sys.exit(65)
    if hadRuntimeError:
        sys.exit(70)
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