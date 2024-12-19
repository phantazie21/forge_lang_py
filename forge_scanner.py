from forge_token import ForgeToken, TokenType
from error import *

class ForgeScanner:

    keywords = {
        "and": TokenType.AND,
        "or": TokenType.OR,
        "class": TokenType.CLASS,
        "if": TokenType.IF,
        "else": TokenType.ELSE,
        "false": TokenType.FALSE,
        "true": TokenType.TRUE,
        "for": TokenType.FOR,
        "while": TokenType.WHILE,
        "fn": TokenType.FUN,
        "null": TokenType.NIL,
        "out": TokenType.PRINT,
        "return": TokenType.RETURN,
        "super": TokenType.SUPER,
        "this": TokenType.THIS,
        "var": TokenType.VAR,
        "break": TokenType.BREAK,
        "continue": TokenType.CONTINUE,
    }
    
    def __init__(self, source, line=1):
        self.source = source
        self.tokens = []
        self.start = 0
        self.current = 0
        self.line = line

    def scanTokens(self):
        while not self.isAtEnd():
            self.start = self.current
            self.scanToken()

        self.tokens.append(ForgeToken(TokenType.EOF, "", None, self.line))
        return self.tokens
    
    def isAtEnd(self):
        return self.current >= len(self.source)
    
    def scanToken(self):
        c = self.advance()
        if c == '(':
            self.addToken(TokenType.LEFT_PAREN)
            return
        elif c == ')':
            self.addToken(TokenType.RIGHT_PAREN)
            return
        elif c == '{':
            self.addToken(TokenType.LEFT_BRACE)
            return
        elif c == '}':
            self.addToken(TokenType.RIGHT_BRACE)
            return
        elif c == "[":
            self.addToken(TokenType.LEFT_BRACKET)
            return
        elif c == "]":
            self.addToken(TokenType.RIGHT_BRACKET)
            return
        elif c == ',':
            self.addToken(TokenType.COMMA)
            return
        elif c == '.':
            self.addToken(TokenType.DOT)
            return
        elif c == '-':
            self.addToken(TokenType.MINUS)
            return
        elif c == '+':
            self.addToken(TokenType.PLUS)
            return
        elif c == ';':
            self.addToken(TokenType.SEMICOLON)
            return
        elif c == '*':
            self.addToken(TokenType.STAR)
            return
        elif c == "%":
            self.addToken(TokenType.MODULO)
            return
        elif c == '!':
            self.addToken(TokenType.BANG_EQUAL if self.match('=') else TokenType.BANG)
            return
        elif c == '=':
            self.addToken(TokenType.EQUAL_EQUAL if self.match('=') else TokenType.EQUAL)
            return
        elif c == '<':
            self.addToken(TokenType.LESS_EQUAL if self.match('=') else TokenType.LESS)
            return
        elif c == '>':
            self.addToken(TokenType.GREATER_EQUAL if self.match('=') else TokenType.GREATER)
            return
        elif c == '/':
            if self.match('/'):
                while self.peek() != '\n' and not self.isAtEnd():
                    self.advance()
            else:
                self.addToken(TokenType.SLASH)
            return
        elif c in [' ', '\r', '\t']:
            return
        elif c == '\n':
            self.line += 1
            return
        elif c == '"':
            self.string()
            return
        elif c.isdigit():
            self.number()
            return
        elif c == "o":
            if self.match("r"):
                self.addToken(TokenType.OR)
                return
        if c.isalpha():
            self.identifier()
        else:
            error(self.line, f"Unexpected character '{c}'.")

    def advance(self):
        ret = self.source[self.current]
        self.current += 1
        return ret
    
    def addToken(self, tokenType, literal=None):
        text = self.source[self.start:self.current]
        self.tokens.append(ForgeToken(tokenType, text, literal, self.line))

    def match(self, expected):
        if self.isAtEnd():
            return False
        if self.source[self.current] != expected:
            return False
        self.current += 1
        return True
    
    def peek(self):
        if self.isAtEnd():
            return '\0'
        return self.source[self.current]
    
    def peekNext(self):
        if self.current + 1 >= len(self.source):
            return '\0'
        return self.source[self.current + 1]
    
    def string(self):
        while self.peek() != '"' and not self.isAtEnd():
            if self.peek() == '\n':
                self.line += 1
            self.advance()
        
        if self.isAtEnd():
            error(self.line, "Unterminated string.")
            return
        
        self.advance()
        value = self.source[self.start+1:self.current-1]
        self.addToken(TokenType.STRING, value)

    def number(self):
        while self.peek().isdigit():
            self.advance()
        
        if self.peek() == "." and self.peekNext().isdigit():
            self.advance()
            while self.peek().isdigit():
                self.advance()

        self.addToken(TokenType.NUMBER, float(self.source[self.start:self.current]))

    def identifier(self):
        while self.peek().isalnum():
            self.advance()

        text = self.source[self.start:self.current]
        _type = self.keywords.get(text)
        if _type == None:
            _type = TokenType.IDENTIFIER
        self.addToken(_type)