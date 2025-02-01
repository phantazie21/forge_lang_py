import sys
import forge_scanner

import forge_parser
from interpreter import Interpreter
from resolver import Resolver
from preprocessor import PreProcessor
from compiler import Compiler
import error

def write_to_file(resolved_statements, filename="output.forgec"):
    with open(filename, "w") as file:
        file.writelines([str(stmt) + "\n" for stmt in resolved_statements])

def read_file(filename="output.forgec"):
    with open(filename, "r") as f:
        return f.read()

interpreter = Interpreter()
resolver = Resolver(interpreter)

def run(source, filename="", compile=False):
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
    if error.hadError:
        return
    
    if not compile:
        interpreter.interpret(expr)
    else:
        compiler = Compiler(expr)
        code = compiler.generate_code()
        write_to_file(code, "output.c")

def runPrompt():
    while True:
        prompt = input("> ")
        if (prompt == ""):
            break
        run(prompt)
        error.hadError = False

def runFile(filename, options):
    if '-c' in options:
        run(open(filename).read(), filename, True)
    else:
        run(open(filename).read(), filename)
    if error.hadError:
        sys.exit(65)
    if error.hadRuntimeError:
        sys.exit(70)

def main():
    '''if len(sys.argv) > 2:
        print("Usage: python main.py <filename>")
        sys.exit(1)'''
    if len(sys.argv) >= 2:
        filename = sys.argv[1]
        options = sys.argv[2:]
        runFile(filename, options)
    else:
        runPrompt()

if __name__ == "__main__":
    main()