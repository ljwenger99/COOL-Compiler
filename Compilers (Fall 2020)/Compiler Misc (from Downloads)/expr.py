from cdcLex import Lexer

def Start(d):
	d.my_var = 0
	return 'EXPR'

def Finish(d):
	if d.my_var == 0: return 'EXPR'
	return 'ERROR', 'Finished with a value of ' + str(d.my_var)

def Sum(d,t):
	d.my_var += int(t.value)
	return None, t # don't switch state and return the token

lexer = Lexer(Start, Finish,
	{ 'EXPR' : [
		('EOL','\n', 'IGNORE'),
		('WHITESPACE', r'\s+', 'IGNORE'),
		('lbrace', r'\{'),
		('rbrace', r'\}'),
		('lparen', r'\('),
		('rparen', r'\)'),
		('NUMBER', r'(\d+)', Sum),
		('OPERATOR', r'([-+*/%^])')]})

print()
tokens = lexer.scan("({^})")
for token in tokens: 
	if token: print(token)

print()
tokens = lexer.scan("(({^})")
for token in tokens: 
	if token: print(token)

print()
tokens = lexer.scan("(){}))((")
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
