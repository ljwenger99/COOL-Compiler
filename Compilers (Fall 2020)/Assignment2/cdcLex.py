import re

class Token(object):
	def __init__(s, type, value, line, pos, text):
		(s.type, s.value, s.line, s.pos, s.text) = (type, value, line, pos, text)
	def __str__(s):
		if s.type == 'ERROR': return s.err() 
		return str(s.line) + ' ' + str(s.pos) + ' ' + s.type + ' ' + (s.value or '')
	def out(self):
		if self.value == None: return '\n'.join((str(self.line),self.type,'')) 
		else: return '\n'.join((str(self.line),self.type,self.value,''))
	def err(self):
		return 'ERROR: %s (line %d, position %d)\n%s%s%s' % (self.value or '', 
			self.line, self.pos, self.text, " " * self.pos, "^")

class Lexer(object):
	def __init__(self, start, finish, rules):
		(self._start, self._finish) = (start, finish)
		(self._states, self._literals) = ({}, {})
		for state in rules.keys():
			x = type('', (), {})() # generic object
			x.patterns = '|'.join('(?P<%s>%s)' % (p[0],p[1]) for p in rules[state])
			(x.res, x.actions) = (re.compile(x.patterns), {})
			for t in rules[state]:
				if len(t) == 3: x.actions[t[0]] = t[2]
				if not re.match(r'\(.*\)$',t[1]):
					p = t[1].replace(r'\b','').replace(r'\A','').replace(r'\B','')
					p = p.replace(r'\Z','').replace('\\','').replace(r'(?i)','')
					y = p.replace(r'(?i:','')
					if len(y) < len(p) : p = y.replace(r')','')
					self._literals[t[0]] = p
			self._states[state] = x
		(self._text, self._line, self._pos) = ('', 0, 0)

	def __str__(self):
		text = 'Literals: ' + '  '.join(n+' '+a for (n,a) in self._literals.items()) 
		for state in self._states.keys():
			x = self._states[state]
			text += '\n' + state + ': ' + x.patterns + '\n\tActions: ' + ' '.join(n +  
				(':' + a if type(a) is str else '') for (n,a) in x.actions.items())
		return text + '\n'

	def _addLine(self, text):
		(self._text, self._pos, self._line) = (text, 0, self._line + 1)
		x = self._states[self._state]
		while True:
			mo = x.res.match(self._text,self._pos)
			if mo == None:
				break
			kind = mo.lastgroup
			self._pos = mo.end(kind)
			value = mo.group(kind)
			t = Token(kind, value, self._line, mo.start(kind), self._text)
			if kind in self._literals: t.value = None
			if kind in x.actions:
				action = x.actions[kind]
				if not type(action) is str:
					action = action(self, t)
					if type(action) is tuple:
						if type(action[1]) is str: t.value = action[1]
						else: t = action[1]
						action = action[0]
					elif action in self._states:
						t = None
				if action in ('IGNORE','IGN', 'I'): t = None
				elif action in ('ERROR', 'ERR', 'E'):
					t.type = 'ERROR'
					yield t, 'ERROR'
					break
				elif action in self._states:
					self._state = action
					x = self._states[action]
					x = self._states[self._state]
				if t == None: continue
			yield t
			if self._pos == len(self._text):
				break
		if self._pos != len(self._text):
			yield Token('ERROR', 'Unexpected character', self._line, self._pos, self._text)


	def scan(self, text):
		if type(self._start) is str:
			self._state = self._start
		else:
			self._state = self._start(self)
		try:
			for line in text.split('\n'):
				for tok in self._addLine(line + '\n'):
					if type(tok) is Token:
						yield tok
					else:
						yield tok[0]
						raise IOError
		except IOError: 
			pass
		if self._pos == len(self._text):
			t = Token('EOD', '', self._line, self._pos - len('\n'), self._text)
			if self._finish:
				if type(self._finish) is str:
					if self._state != self._finish:
						(t.type, t.value) = ('ERROR', 'Unexpected end of data')
				else:
					result = self._finish(self)
					if type(result) is tuple:
						(t.type, t.value) = (result[0], result[1])
					elif self._state != result:
						(t.type, t.value) = ('ERROR', 'Unexpected end of data')
					else: return
			yield t

	def unscan(self, text):
		tokens = text.split('\n')
		line = 1
		data = ''
		while tokens:
			n = tokens.pop(0)
			if not n: break
			if int(n) > line:
				data += '\n'
				line = int(n)
			n = tokens.pop(0)
			if n in self._literals:
				data += self._literals[n] + ' '
				continue
			n = tokens.pop(0)
			data += n + ' '
		return data + '\n'
