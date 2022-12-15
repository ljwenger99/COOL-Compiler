from cdcLex import Lexer

def Start(d):
        d.pbtracker = []
        return 'EXPR'

def Finish(d):
        if d.pbtracker != []:
            return 'ERROR', 'Number of open parenthesis/braces exceeds number of closed parenthesis/braces.'
        else:
            return 'EXPR'


def ErrorCheck(d,t):
    if str(t.type) in ["lbrace","lparen"]:
        '''
        IF YOU WANTED TO ALWAYS START WITH PARENTHESIS AND RAISE AN ERROR IF YOU START WITH BRACES,
        YOU COULD USE THE COMMENTED CODE BELOW:
        (THIS ISN'T THE MOST EFFICIENT WAY TO IMPLEMENT THIS ERROR, BUT IT ALLOWS IT TO BE COMMENTED OUT EASILY)
        '''
        #if d.pbtracker == [] and str(t.type) == "lbrace":
            #return 'ERROR', 'Must use parenthesis in outer shell.'
        if d.pbtracker == []:
            d.pbtracker.append(str(t.type))
        elif d.pbtracker[-1] != str(t.type):
            d.pbtracker.append(str(t.type))
        else:
            return 'ERROR', 'Parenthesis and braces must alternate.'
    elif str(t.type) in ["rbrace","rparen"]:
        if d.pbtracker == []:
            return 'ERROR', 'No open parenthesis/braces to close.'
        elif str(t.type) == "rparen":
            if d.pbtracker[-1] == "lparen":
                d.pbtracker = d.pbtracker[:-1]
            else:
                return 'ERROR', 'Brace must be closed before parenthesis.'
        elif str(t.type) == "rbrace":
            if d.pbtracker[-1] == "lbrace":
                d.pbtracker = d.pbtracker[:-1]
            else:
                return 'ERROR', 'Parenthesis must be closed before brace.'
    return None, t
         
    
lexer = Lexer(Start, Finish,
	{ 'EXPR' : [
		('EOL','\n', 'IGNORE'),
		('WHITESPACE', r'\s+', 'IGNORE'),
		('lbrace', r'\{', ErrorCheck),
		('rbrace', r'\}', ErrorCheck),
		('lparen', r'\(', ErrorCheck),
		('rparen', r'\)', ErrorCheck),
		('NUMBER', r'(\d+)'),
		('OPERATOR', r'([-+*/%^])')]})



tokens = lexer.scan("(5")
for token in tokens:
        if token.type == 'ERROR':
                print((str(token.type)) + ': ' + (str(token.line)) + ': Lexer : ' + (str(token.value)))

print()
tokens = lexer.scan("({)}")
for token in tokens: 
	if token: print(token)
