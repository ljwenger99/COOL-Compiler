from cdcLex import Lexer

def Start(d):
        d.pbtracker = []
        return 'EXPR'

def Finish(d):
        if d.pbtracker != []:
            return 'ERROR', 'Number of open parenthesis exceeds number of closed parenthesis.'
        else:
            return 'EXPR'


def ErrorCheck(d,t):
    if str(t.type) == 'lparen':
        d.pbtracker.append(str(t.type))
    if str(t.type) == 'rparen':
        if d.pbtracker == []:
            return 'ERROR', 'No open parenthesis to close.'
        else:
            d.pbtracker = d.pbtracker[:-1]
    return None, t        

lexer = Lexer(Start, Finish,
	{ 'EXPR' : [
		('EOL','\n', 'IGNORE'),
		('WHITESPACE', r'\s+', 'IGNORE'),
		('lbrace', r'\{'),
		('rbrace', r'\}'),
		('lparen', r'\(', ErrorCheck),
		('rparen', r'\)', ErrorCheck),
		('NUMBER', r'(\d+)'),
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

print()
tokens = lexer.scan("({)}")
for token in tokens: 
	if token: print(token)



