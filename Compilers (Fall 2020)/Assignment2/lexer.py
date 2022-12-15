#Lucas Wenger
from cdcLex import Lexer
import sys

def Start(d):
        d.pbtracker = []
        return 'INITIAL'

def Finish(d):
        if d.pbtracker != []:
            return 'ERROR', 'Some parenthesis/braces left open.'
        else:
            return 'INITIAL'


def ErrorCheck(d,t):#Deals with parentehsis and braces
    if str(t.type) in ["lbrace","lparen"]:
        d.pbtracker.append(str(t.type))
    if str(t.type) in ["rbrace","rparen"]:
        if d.pbtracker == []:
            t.type = 'ERROR'
            t.value = 'No open parenthesis/braces to close.'
        elif str(t.type) == "rparen":
            if d.pbtracker[-1] == "lparen":
                d.pbtracker = d.pbtracker[:-1]
            else:
                t.type = 'ERROR'
                t.value = 'Brace must be closed before parenthesis.'
        elif str(t.type) == "rbrace":
            if d.pbtracker[-1] == "lbrace":
                d.pbtracker = d.pbtracker[:-1]
            else:
                t.type = 'ERROR'
                t.value = 'Parenthesis must be closed before brace.'
    return None, t

def StartString(d,t):
	d.string_text = ''
	d.string_start_line = t.line
	d.string_start_pos = t.pos
	return 'STRING'

def BuildString(d,t):
	d.string_text += t.value
	return 'IGNORE'

def EndString(d,t):
	t.value = d.string_text
	t.line = d.string_start_line
	t.pos = d.string_start_pos
	return 'INITIAL', t

def StartComment(d,t):
        return 'COMMENT'

def EndComment(d,t):
	return 'INITIAL'

def IntegerChecker(d,t):
        if int(t.value) > 2147483647:
            t.type = 'ERROR'
            t.value = 'Integer too large to be supported by COOL.'
        return None, t
    
    
lexer = Lexer(Start, Finish,
	{ 'INITIAL' : [
		('EOL', r'(\n)', 'IGNORE'),
		('WHITESPACE', r'(\s+)', 'IGNORE'),
		('lbrace', r'(\{)', ErrorCheck),
		('rbrace', r'(\})', ErrorCheck),
		('lparen', r'(\()', ErrorCheck),
		('rparen', r'(\))', ErrorCheck),
		('integer', r'(\d+)', IntegerChecker), #no larger than 2147483647
                ('startstring', r'(\")', StartString), 
                ('startcomment', r'(/\*)', StartComment), 
                ('eolcomment', r'(\-\-.*\n)', 'IGNORE'),
                ('class', r'((?i:class)\b)'),
                ('else', r'((?i:else)\b)'),
                ('false', r'((?i:alse)\b)'),
                ('fi', r'((?i:fi)\b)'),
                ('if', r'((?i:if)\b)'),
                ('in', r'((?i:in)\b)'),
                ('inherits', r'((?i:inherits)\b)'),
                ('isvoid', r'((?i:isvoid)\b)'),
                ('let', r'((?i:let)\b)'),
                ('loop', r'((?i:loop)\b)'),
                ('pool', r'((?i:pool)\b)'),
                ('then', r'((?i:then)\b)'),
                ('while', r'((?i:while)\b)'),
                ('case', r'((?i:case)\b)'),
                ('esac', r'((?i:esac)\b)'),
                ('new', r'((?i:new)\b)'),
                ('of', r'((?i:of)\b)'),
                ('not', r'((?i:not)\b)'),
                ('true', r'((?i:rue)\b)'),
                ('at', r'(\@)'),
                ('Add', r'(\+)'),
                ('Subtract', r'(\-)'),
                ('Multiply', r'(\*)'),
                ('Divide', r'(\/)'),
                ('rarrow', r'(\=\>)'),
                ('larrow', r'(\<\-)'),
                ('le', r'(\<\=)'),
                ('lt', r'(\<)'),
                ('equal', r'(\=)'),
                ('colon', r'(\:)'),
                ('comma', r'(\,)'),
                ('semi', r'(\;)'),
                ('tilde', r'(\~)'),
                ('dot', r'(\.)'),
                ('identifier', r'([a-z][_a-zA-Z0-9]*)'),
                ('type', r'([A-Z][_a-zA-Z0-9]*)')
                ],
          'COMMENT' : [
                ('endcomment', r'(\*/)', EndComment),
                ('commenttext', r'(.|\n)', 'IGNORE')
                ],
          'STRING' : [
                ('string', r'\"', EndString),
                ('internalquote', r'(\\\")', BuildString),
                ('stringtext', r'(.|\n)', BuildString)
                ]})


while True:
    outstring = ''#By building the string here first, we can avoid creating a new file if there are any errors in the original cool program. 
    error = False
    #coolfile = input('Enter COOL file name: \n')#Comment in to use with python interpreter rather than command line
    coolfile = sys.argv[1]#Comment out to use with python interpreter rather than command line
    #if coolfile == 'close':#Also not necessary if using command line
        #break
    with open(coolfile, 'r') as file:
        tokens = lexer.scan(file.read()+'\n') #Turns out that the "Finish" parenthesis check can't run if there is an error on the final line. This extra line prevents that from being an issue.
    for token in tokens:
        if token.type == 'ERROR':
            print((str(token.type)) + ': ' + (str(token.line)) + ': Lexer : ' + (str(token.value))) #Based on standard COOL error reporting
            error = True
        else:
            if token.type in ('string','integer','identifier','type'):
                outstring += (str(token.line)+'\n' + str(token.type)+'\n' + str(token.value)+'\n') #Based on COOL output formatting
            else:
                outstring += (str(token.line)+'\n' + str(token.type)+'\n')
    if error == False:
        with open(coolfile + '-lex', 'w') as newfile:
            print('New file \"' + coolfile + '-lex\" created.\n')
            newfile.write(outstring)
    break#Could replace with continue if not using single command line
        
