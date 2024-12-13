import sys
import forge_scanner
import error
import forge_parser
from interpreter import Interpreter

def run(source):
    scanner = forge_scanner.ForgeScanner(source)
    tokens = scanner.scanTokens()
    if error.hadError:
        return
    parser = forge_parser.Parser(tokens)
    expr = parser.parse()
    if error.hadError:
        return
    interpreter = Interpreter()
    interpreter.interpret(expr)
    if error.hadRuntimeError:
        return

def runPrompt():
    while True:
        prompt = input("> ")
        if (prompt == ""):
            break
        run(prompt)
        error.hadError = False
        error.hadRuntimeError = False

def runFile(filename):
    run(open(filename).read())
    if error.hadError:
        sys.exit(70)
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

main()