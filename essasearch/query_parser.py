import re
from typing import List, Union

class TokenType:
    TERM = "TERM"
    AND = "AND"
    OR = "OR"
    NOT = "NOT"
    LPAREN = "LPAREN"
    RPAREN = "RPAREN"

class Token:
    def __init__(self, type: str, value: str):
        self.type = type
        self.value = value
    def __repr__(self):
        return f"Token({self.type}, '{self.value}')"

class ASTNode:
    pass

class TermNode(ASTNode):
    def __init__(self, field: str, value: str):
        self.field = field  # None if default 'content' field
        self.value = value
    def __repr__(self):
        if self.field:
            return f"Term({self.field}:{self.value})"
        return f"Term({self.value})"

class AndNode(ASTNode):
    def __init__(self, left: ASTNode, right: ASTNode):
        self.left = left
        self.right = right
    def __repr__(self):
        return f"AND({self.left}, {self.right})"

class OrNode(ASTNode):
    def __init__(self, left: ASTNode, right: ASTNode):
        self.left = left
        self.right = right
    def __repr__(self):
        return f"OR({self.left}, {self.right})"

class NotNode(ASTNode):
    def __init__(self, node: ASTNode):
        self.node = node
    def __repr__(self):
        return f"NOT({self.node})"

class QueryLexer:
    """Tokenizes a query string into a sequence of Tokens."""
    def tokenize(self, query: str) -> List[Token]:
        tokens = []
        # Extract quoted strings or regular tokens
        # We also need to handle field:value syntax.
        # This regex matches: parenthesis, OR, AND, NOT, field:value, or regular terms
        pattern = re.compile(r'(\()|(\))|\b(AND)\b|\b(OR)\b|\b(NOT)\b|([a-zA-Z0-9_]+:[a-zA-Z0-9_]+)|(\b\w+\b)')
        
        matches = pattern.finditer(query)
        for match in matches:
            lparen, rparen, op_and, op_or, op_not, field_val, term = match.groups()
            if lparen:
                tokens.append(Token(TokenType.LPAREN, lparen))
            elif rparen:
                tokens.append(Token(TokenType.RPAREN, rparen))
            elif op_and:
                tokens.append(Token(TokenType.AND, op_and))
            elif op_or:
                tokens.append(Token(TokenType.OR, op_or))
            elif op_not:
                tokens.append(Token(TokenType.NOT, op_not))
            elif field_val:
                tokens.append(Token(TokenType.TERM, field_val))
            elif term:
                tokens.append(Token(TokenType.TERM, term))
        return tokens

class QueryParser:
    """
    Recursive descent parser that converts a list of tokens into an AST.
    Grammar:
        query  -> expr
        expr   -> term (OR term)*
        term   -> factor (AND factor)* | factor factor* (implicit OR for sequence of terms)
        factor -> NOT factor | LPAREN expr RPAREN | TERM
    """
    def __init__(self):
        self.tokens = []
        self.pos = 0

    def parse(self, query: str) -> ASTNode:
        lexer = QueryLexer()
        self.tokens = lexer.tokenize(query)
        self.pos = 0
        if not self.tokens:
            return None
        return self._parse_expr()

    def _current_token(self) -> Token:
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def _consume(self, expected_type=None):
        token = self._current_token()
        if expected_type and (not token or token.type != expected_type):
            raise ValueError(f"Expected {expected_type}, got {token.type if token else 'EOF'}")
        self.pos += 1
        return token

    def _parse_expr(self) -> ASTNode:
        # expr -> term (OR term)*
        node = self._parse_term()
        
        while self._current_token() and self._current_token().type == TokenType.OR:
            self._consume(TokenType.OR)
            right = self._parse_term()
            node = OrNode(node, right)
            
        return node

    def _parse_term(self) -> ASTNode:
        # term -> factor (AND factor)* | factor factor* (implicit OR, but implicit AND for NOT)
        node = self._parse_factor()
        
        while self._current_token() and self._current_token().type in (TokenType.AND, TokenType.TERM, TokenType.LPAREN, TokenType.NOT):
            if self._current_token().type == TokenType.AND:
                self._consume(TokenType.AND)
                right = self._parse_factor()
                node = AndNode(node, right)
            elif self._current_token().type == TokenType.NOT:
                right = self._parse_factor()
                node = AndNode(node, right) # Implicit AND for NOT (fox NOT dog -> fox AND NOT dog)
            else:
                # Implicit OR for sequence of terms like "fast fox" -> OR(fast, fox)
                right = self._parse_factor()
                node = OrNode(node, right)
                
        return node

    def _parse_factor(self) -> ASTNode:
        # factor -> NOT factor | LPAREN expr RPAREN | TERM
        token = self._current_token()
        if not token:
            raise ValueError("Unexpected EOF")
            
        if token.type == TokenType.NOT:
            self._consume(TokenType.NOT)
            child = self._parse_factor()
            return NotNode(child)
            
        if token.type == TokenType.LPAREN:
            self._consume(TokenType.LPAREN)
            node = self._parse_expr()
            self._consume(TokenType.RPAREN)
            return node
            
        if token.type == TokenType.TERM:
            self._consume(TokenType.TERM)
            val = token.value
            if ':' in val:
                field, term_val = val.split(':', 1)
                return TermNode(field, term_val)
            return TermNode(None, val)
            
        raise ValueError(f"Unexpected token: {token}")
