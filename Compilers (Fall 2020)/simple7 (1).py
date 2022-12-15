from cdcLex import Lexer

def StartComment(d,t):
	d.comment_text = ''
	d.comment_start_line = t.line
	d.comment_start_pos = t.pos
	return 'COMMENT'

def BuildComment(d,t):
	d.comment_text += t.value
	return 'IGNORE'

def EndComment(d,t):
	t.value = d.comment_text
	t.line = d.comment_start_line
	t.pos = d.comment_start_pos
	return 'INITIAL', t

def FinishState(d):
	if d._state == 'INITIAL':
		return 'DONE', 'Scan successful'
	return 'INITIAL'

lexer = Lexer('INITIAL', FinishState, 
	{"INITIAL" : [
		('WHITESPACE', r'[ \t\n]+', 'IGNORE'),
		('NUM', r'(\d+)'),
		('ID', r'([a-zA-Z_]+)'),
		('PLUS', r'\+'),
		('COMMA', r','),
		('COMMENTSTART', r'/\*', StartComment)],
	"COMMENT" : [
		('COMMENTEND', r'(\*/)', EndComment),
		('COMMENTTEXT', r'(.|\n)', BuildComment)]})

tokens = lexer.scan('x+3,  /* /* 5, */ 2')
for tok in tokens:
	print(tok)
print()

