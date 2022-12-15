from cdcLex import Lexer

def Expr(d):
	return 'EXPR'

lexer = Lexer(Expr, Expr,
	{ 'EXPR' : [
		('EOL','\n', 'IGNORE'),
		('WHITESPACE', r'\s+', 'IGNORE'),
		('lbrace', r'\{'),
		('rbrace', r'\}'),
		('lparen', r'\('),
		('rparen', r'\)'),
		('NUMBER', r'(\d+)'),
		('OPERATOR', r'([-+*/%^])')]})


print()
tokens = lexer.scan("(({4 5})")
for token in tokens: 
	if token: print(token)

print()
tokens = lexer.scan("({4 5})")
for token in tokens: 
	if token: print(token)

print()
tokens = lexer.scan("(){}")
for token in tokens: 
	if token: print(token)

print()
tokens = lexer.scan("x")
for token in tokens: 
	if token: print(token)

print()
tokens = lexer.scan("3 + 4")
for token in tokens: 
	if token: print(token)

print()
tokens = lexer.scan("(5")
for token in tokens: 
	if token: print(token)
