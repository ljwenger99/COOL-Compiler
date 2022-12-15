import sys

''' 
# A framework for implementing A5

# API

# (ctab,ast) = read_AAST(filename) # read in the .cl-type file structures
# 
# AST Expression nodes always start with a line number, a type, and a tag
# The tag identifies the type of expresion (i.e. plus, let, if, etc.)
# The type field is initially set to None for all expressions.
# Other variant nodes (method, attribute, dispatch) will pad with None for optionals
#
# ClassTab class - a class symbol table, generates serialized map of class data
#
#   get_class(name) # returns the class name or None if it isn't defined
#   get_parent(name) # returns the name of the parent class (or None)
#	all_classes() # returns a list of the all registered classes (including Object)
#	declared_methods(name) # only the locally declared methods for the class
#   get_attribute(cname, aname) # returns the attribute defined in the class (or #   find_attribute(cname, aname) # returns an attribute (possibility inherited) for the class (or None)
#   get_method(cname, mname) # returns the method defined in the class (or None)
#   find_method(cname, mname) # returns a method (possibility inherited) for the class (or None)
#
# SymTab class - a simple symbol table (used when processing expressions)
#   add_symbol(name,data) # add a new symbol and data to associate with it
#	find_symbol(name) # returns the previously associated data (or None)
#	is_in_scope(name) # like find_symbol but only finds local variables
#	enter_scope()	# create a new scope for local variables
#	clear_scope()	# return to previous scope clearing all of the local variables
#
'''

'''
##### Format Helpers

def format_list(a, format_function):
	text = str(len(a)) + "\n"
	for i in range(len(a)):
		text += format_function(a[i])
	return text

def format_id(a):
	return str(a[0]) + "\n" + a[1] + "\n"

def format_formal(a):
	return format_id(a[0]) + format_id(a[1])

def format_expr(a):
	if not a or a == None: return ""
	text = a[0] + "\n" 
	if a[1] != None: text += a[1] + "\n"
	text += a[2] + "\n"
	if a[2] in ['assign']:
		text += format_id(a[3]) + format_expr(a[4])
	elif a[2] in ['dynamic_dispatch']:
		text += format_expr(a[3]) + format_id(a[5])
		text += format_list(a[6], format_expr)
	elif a[2] in ['static_dispatch']:
		text += format_expr(a[3]) + format_id(a[4])
		text += format_id(a[5]) + format_list(a[6], format_expr)
	elif a[2] in ['self_dispatch']:
		text += format_id(a[5]) + format_list(a[6], format_expr)
	elif a[2] in ['if']:
		text += format_expr(a[3]) + format_expr(a[4]) + format_expr(a[5])
	elif a[2] in ['block']:
		text +=	format_list(a[3], format_expr)
	elif a[2] in ['new', 'identifier']:
		text += format_id(a[3])
	elif a[2] in ['integer', 'string']:
		text += a[3] + "\n"
	elif a[2] in ['true', 'false']:
		pass
	elif a[2] in ['negate', 'not', 'isvoid']:
		text += format_expr(a[3])
	elif a[2] in ['while','plus','minus','times','divide','lt','le','eq']:
		text += format_expr(a[3]) + format_expr(a[4])
	elif a[2] in ['let']:
		text += format_list(a[3],format_let_binding) + format_expr(a[4])
	elif a[2] in ['case']:
		text += format_expr(a[3]) + format_list(a[4],format_case_element)
	else:
		print('Unrecognized expression', a)
		exit()
	return text

def format_let_binding(a):
	text = a[0] + "\n" + format_id(a[1]) + format_id(a[2])
	if a[0] == 'let_binding_init':
		text += format_expr(a[3])
	return text

def format_case_element(a):
	return format_id(a[0]) + format_id(a[1]) + format_expr(a[2])

def format_feature(a):
	text = a[0] + "\n" + format_id(a[1])
	if a[0] == 'method':
		text += format_list(a[2],format_formal)
		text += format_id(a[3]) + format_expr(a[4])
	else:
		text += format_id(a[2])
		if a[0] == 'attribute_init':
			text += format_expr(a[3])
	return text

def format_class(a):
	text = format_id(a[0]) + a[1] + "\n" 
	if a[1] == 'inherits':
		text += format_id(a[2])
	text += format_list(a[3],format_feature)
	return text

def format_program(a):
	return format_list(a, format_class)

'''

#### Class Table for tracking classes and generating the three maps
class ClassTab():

	def __init__(self):
		self.data = {}
		self.data['Object'] = { 
			'parent': None,
			'attribs': [],
			'methods': [
				('abort', [], ('0','Object'), ('0','Object','internal','Object.abort'), 'Object'),
				('copy', [], ('0','SELF_TYPE'), ('0','SELF_TYPE','internal','Object.copy'), 'Object'),
				('type_name', [], ('0','String'), ('0','String', 'internal','Object.type_name'), 'Object')]}
		self.data['Bool'] = {
			'parent': 'Object',
			'attribs': [],
			'methods': []}
		self.data['Int'] = {
			'parent': 'Object',
			'attribs': [],
			'methods': []}
		self.data['IO'] = {
			'parent': 'Object',
			'attribs': [],
			'methods': [
				('in_int', [], ('0','IO'), ('0','Int','internal','IO.in_int'), 'IO'),
				('in_string', [], ('0','IO'), ('0','String','internal','IO.in_string'), 'IO'),
				('out_int', [('x','Int')], ('0','IO'), ('0','SELF_TYPE','internal','IO.out_int'), 'IO'),
				('out_string', [('x','String')], ('0','IO'), ('0','SELF_TYPE','internal','IO.out_string'), 'IO')]}
		self.data['String'] = {
			'parent': 'Object',
			'attribs': [],
			'methods': [
				('concat', [('s','String')], ('0','String'), ('0','String','internal','String.concat'), 'String'),
				('length', [], ('0','Int'), ('0','Int','internal','String.length'), 'String'),
				('substr', [('i','Int'),('l','Int')], ('0','String'), ('0','String','internal','String.substr'), 'String')]}

	def add_class(self, name, parent_name):
		if name in self.data: return None
		if parent_name == None: parent_name = 'Object'
		self.data[name] = { 'parent': parent_name, 'attribs': [], 'methods': [] }
		return self

	def get_class(self, name):
		if name in self.data:
			return name
		return None

	def get_parent(self, name):
		if name in self.data:
			return self.data[name]['parent']
		return None

	def all_classes(self):
		return sorted(self.data.keys())
			
	def add_attribute(self, cname, aname, type, init):
		self.data[cname]['attribs'].append((aname, type, init))
		return self

	def get_attribute(self, cname, aname):
		for a in self.data[cname]['attribs']:
			if a[0][1] == aname: return a
		return None

	def find_attribute(self, cname, aname):
		if cname == None: return None
		a = self.get_attribute(cname, aname)
		if a != None: return a
		return self.find_attribute(self.get_parent(cname), aname)

	def all_attributes(self, name):
		if name == None: return []
		overrides = {}
		alist = []
		for i in self.all_attributes(self.get_parent(name)):
			x = self.get_attribute(name, i[0][1])
			if x == None:
				alist.append(i)
			else:
				alist.append(x)
				overrides[x[0]] = True
		for a in self.data[name]['attribs']:
			if a[0] in overrides: continue
			alist.append(a)
		return alist

	def inherited_attributes(self, name):
		if name == None: return []
		return self.all_attributes(self.get_parent(name))


	def add_method(self, cname, mname, args, type, body):
		self.data[cname]['methods'].append((mname, args, type, body, cname))
		return self

	def get_method(self, cname, mname):
		for m in self.data[cname]['methods']:
			if m[0] == mname: return m
		return None

	def find_method(self, cname, mname):
		if cname == None: return None
		m = self.get_method(cname, mname)
		if m != None: return m
		return self.find_method(self.get_parent(cname), mname)

	def all_methods(self, name):
		if name == None: return []
		overrides = {}
		mlist = []
		for i in self.all_methods(self.get_parent(name)):
			x = self.get_method(name, i[0])
			if x == None:
				mlist.append(i)
			else:
				mlist.append(x)
				overrides[x[0]] = True
		for m in self.data[name]['methods']:
			if m[0] in overrides: continue
			mlist.append(m)
		return mlist

	def declared_methods(self, name):
		return self.data[name]['methods']

	def inherited_methods(self, name):
		if name == None: return []
		return self.all_methods(self.get_parent(name))

	def parent_map(self):
		text = ['parent_map', str(len(self.data)-1)]  # don't include object
		for i in sorted(self.data.keys()):
			if i == 'Object': continue
			text.append(i)
			text.append(self.data[i]['parent'])
		return "\n".join(text)

	def class_map(self):
		text = ['class_map', str(len(self.data))]
		for i in sorted(self.data.keys()):
			text.append(i)
			attributes = self.all_attributes(i)
			text.append(str(len(attributes)))
			for a in attributes:
				if a[2] == None: text.append("no_initializer")
				else: text.append("initializer")
				text.append(a[0][1])
				text.append(a[1][1])
				text.append(format_expr(a[2]).rstrip("\n"))
		return "\n".join(text)

	def implementation_map(self):
		text = ['implementation_map', str(len(self.data))]
		for i in sorted(self.data.keys()):
			text.append(i)
			methods = self.all_methods(i)
			text.append(str(len(methods)))
			for m in methods:
				text.append(m[0])
				text.append(str(len(m[1])))
				for f in m[1]:
					text.append(f[0])
				text.append(m[4])  # defining class not the return type
				if len(m[3]) == 4 and m[3][0] == '0' and m[3][2] == 'internal':
					text += m[3]
				else:
					text.append(format_expr(m[3]).rstrip("\n"))
		return "\n".join(text)

##### A Simple Symbol Table
class SymTab():
	def __init__(self):
		self.data = []

	def add_symbol(self, name, data):
		self.data.append((name, data))

	def enter_scope(self):
		self.data.append(("SCOPE",None))

	def clear_scope(self):
		i = len(self.data) - 1
		while i > 0 and (self.data[i])[0] != "SCOPE":
			i -= 1
		self.data = self.data[0:i]

	def find_symbol(self, name):
		for (n,d) in reversed(self.data):
			if n == name:
				return (n, d)
		return None

	def is_in_scope(self, name):
		for (n,d) in reversed(self.data):
			if n == name:
				return (n, d)
			if n == "SCOPE":
				return None
		return None

##### DESERIALIZE TYPE FILE
def read_AAST(filename):

	def get_line():
		return file.readline().rstrip("\n\r")

	def get_list(get_function):
		list = []
		for i in range(int(get_line())):
			list.append(get_function())
		return list

	def get_id():
		line = get_line()
		id = get_line()
		#print(line, id)
		return (line, id)

	def get_formal():
		name = get_id()
		type = get_id()
		return (name, type)

	def get_expr():
		line = get_line()
		type = get_line()
		tag = get_line()
		#print(line,tag)
		if tag in ['assign']:
			var = get_id()
			rhs = get_expr()
			return [line, type, tag, var, rhs]
		elif tag in ['dynamic_dispatch']:
			exp = get_expr()
			method = get_id()
			args = get_list(get_expr)
			return [line, type, tag, exp, None, method, args]
		elif tag in ['static_dispatch']:
			exp = get_expr()
			type = get_id()
			method = get_id()
			args = get_list(get_expr)
			return [line, type, tag, exp, type, method, args]
		elif tag in ['self_dispatch']:
			method = get_id()
			args = get_list(get_expr)
			return [line, type, tag, None, None, method, args]
		elif tag in ['if']:
			prd = get_expr()
			thn = get_expr()
			els = get_expr()
			return [line, type, tag, prd, thn, els]
		elif tag in ['block']:
			body = get_list(get_expr)
			return [line, type, tag, body]
		elif tag in ['new', 'identifier']:
			name = get_id()
			return [line, type, tag, name]
		elif tag in ['integer', 'string']:
			value = get_line()
			return [line, type, tag, value]
		elif tag in ['true', 'false']:
			return [line, type, tag]
		elif tag in ['negate', 'not', 'isvoid']:
			exp = get_expr()
			return [line, type, tag, exp]
		elif tag in ['while','plus','minus','times','divide','lt','le','eq']:
			exp1 = get_expr()
			exp2 = get_expr()
			return [line, type, tag, exp1, exp2]
		elif tag in ['let']:
			binding = get_list(get_let_binding)
			body = get_expr()
			return [line, type, tag, binding, body]
		elif tag in ['case']:
			exp = get_expr()
			elementslist = get_list(get_case_element)
			return [line, type, tag, exp, elementslist]
		elif tag in ['internal']:
			parent = get_line()
			return [line, type, tag, parent]
		else:
			print('Unrecognized expression', line, tag)
			exit()

	def get_let_binding():
		bind = get_line()
		var = get_id()
		type = get_id()
		exp = None
		if bind == 'let_binding_init':
			exp = get_expr()
		return (bind, var, type, exp)

	def get_case_element():
		var = get_id()
		type = get_id()
		body = get_expr()
		return (var,type,body)

	def get_feature():
		tag = get_line()
		name = get_id()
		if tag == 'method':
			formalslist = get_list(get_formal)
			type = get_id()
			body = get_expr()
			return (tag, name, formalslist, type, body)
		else:
			type = get_id()
			init = None
			if tag == 'attribute_init':
				init = get_expr()
			return (tag, name, type, init)

	def get_class():
		name = get_id()
		tag = get_line()
		parent = None
		if tag == 'inherits':
			parent = get_id()
		featurelist = get_list(get_feature)
		return (name, tag, parent, featurelist)

	def get_class_map_attrib():
		tag = get_line()
		name = get_line()
		type = get_line()
		init = None
		if tag == "initializer":
			init = get_expr()
		return (tag, (0,name), (0,type), init)

	def get_class_map():
		name = get_line()
		attribs = get_list(get_class_map_attrib)
		return (name, attribs)

	def get_implementation_map_method():
		name = get_line()
		formals = get_list(get_line)
		type = get_line()
		body = get_expr()
		return (name, formals, type, body)

	def get_implementation_map():
		name = get_line()
		methods = get_list(get_implementation_map_method)
		return (name, methods)

	def get_parent_map():
		name = get_line()
		parent = get_line()
		return (name, parent)

	# read_AST function body
	file = open(filename)
	get_line()
	class_map = get_list(get_class_map) # attributes
	get_line()
	implementation_map = get_list(get_implementation_map) # methods
	get_line()
	parent_map = get_list(get_parent_map) # methods
	program_classlist = get_list(get_class) # annotated tree

	ctab = ClassTab()
	for (cname,parent) in parent_map:
		ctab.add_class(cname,parent)
	for (cname, attrs) in class_map:
		for a in attrs:
			ctab.add_attribute(cname, a[1], a[2], a[3])
	for (cname, methods) in implementation_map:
		for m in methods:
			if not ctab.find_method(cname, m[0]):
				ctab.add_method(cname, m[0], m[1], m[2], m[3])
	file.close()
	return ctab, program_classlist


filename = 'test'

(ctab, ast) = read_AAST(filename + '.cl-type')

'''
# Re-output the .cl-type file to verify structures are being read in correctlyf = open(filename + '.cl-type5','w')
f.write(ctab.class_map() + "\n")
f.write(ctab.implementation_map() + "\n")
f.write(ctab.parent_map() + "\n")
f.write(format_program(ast))
f.close()

f1 = open(filename + '.cl-type')
f2 = open(filename + '.cl-type5')
for d in f1:
	if d != f2.readline():
		print("ERROR: Problem reading .cl-type file")
		exit()
'''

print(ast)

stab = SymTab()

# r0 - self
# r1 - result/accumulator
# r2 - temp
f = open(filename + '.cl-asm','w')

# placeholder attributes/types for boxed types
ctab.add_attribute("Bool", (0,"X"), (0, "unboxed"), 0)
ctab.add_attribute("Int", (0,"X"), (0, "unboxed"), 0)
ctab.add_attribute("String", (0,"X"), (0, "unboxed"), 0)

# constant string literals
string_table = {}
string_count = 0
def string_cache(value):
	global string_table
	global string_count
	if not value in string_table:
		string_table[value] = "string" + str(string_count)
		string_count = string_count + 1
	return string_table[value]
	
string_cache("")



def asm(instr, comment = ""):
	if instr[-1] == ":": # label
		if len(comment) > 0 and comment[0] == ';':
			f.write("%24s;; ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;\n" % "");
		f.write("%-24s%s\n" % (instr, comment))
	elif comment:
		f.write("%24s%s\t;; %s\n" % ("",instr,comment))
	else:
		f.write("%24s%s\n" % ("",instr))

def asp(instr, comment = ""):
	if instr[-1] == ":":
		print("%s;; ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;" % "\t");
		print("%s%s" % (instr, comment))
	elif comment:
		print("%s%s\t;; %s" % ("\t",instr,comment))
	else:
		print("%s%s" % ("\t",instr))




# BEGINNING OF CODE GENERATION


# vtables for all classes
for cname in sorted(ctab.all_classes()):
	# create label using double dots for name mangling (ensure uniqueness)
	asm("%s..vtable:" % cname, ";; virtual function table for %s" % cname)
	asm("constant %s" % string_cache(cname)) # class name for run-time introspection
	asm("constant %s..new" % cname) # constructor method is never declared in Cool
	for m in ctab.all_methods(cname):  # all other methods
		asm("constant %s.%s" % (m[4],m[0])) # declaring object + method names

	
# r0 - self
# r1 - result/accumulator
# r2 - temp

casenum = 0
ltiteration = 0
ifiteration = 0
notiteration = 0

# support routine
# always returns location of result in r1
def code_gen_expr(e):
        if e == None: return None
        type = e[1]
        tag = e[2]
        if tag == 'identifier':
                asm("ld r1 <- %s" % stab.find_symbol(e[3][1])[1], "offset of %s" % e[3][1])
        elif tag == 'integer': # literal integer needs to be boxed
                code_gen_expr([0,"Int","new",(0,"Int")]) # create the box object
                asm("li r2 <- %s" % e[3]) # literal value
                asm("st r1[1] <- r2") # store value in the box object
        elif tag == 'string': # literal string needs to be boxed
                code_gen_expr([0,"String","new",(0,"String")]) # create the box object
                asm("la r2 <- %s" % string_cache(e[3])) # literal value
                asm("st r1[1] <- r2") # store value in the box object
        elif tag == 'new': # new calls constructor based on type name
                asm("push fp") # call setup
                asm("push r0")
                asm("la r2 <- %s..new" % e[3][1])
                asm("call r2", "create the new object (in r1)")
                asm("pop r0") # call cleanup
                asm("pop fp")
        elif tag == 'plus': # operands are both Int values
                code_gen_expr(e[3]) # first operand object to r1
                asm("ld r2 <- r1[1]", "value from Int") # value from heap
                asm("push r2")
                code_gen_expr(e[4]) # second operand object to r1
                asm("pop r2")
                asm("ld r1 <- r1[1]", "value from Int") # value from heap
                asm("add r2 <- r2 r1") # the add operation
                asm("push r2") # store value on the stack
                code_gen_expr([0,"Int","new",(0,"Int")]) # construct a new integer object
                asm("pop r2")
                asm("st r1[1] <- r2", "plus result in returned object") # put the value into the new object
#ADDED TAGS:-------------------------------------------------------------------------------------------------------

        elif tag == 'true':
                code_gen_expr([0, "Bool","new",(0,"Bool")]) # create the box object
                asm("li r2 <- 1") # Value is 1 if true
                asm("st r1[1] <- r2")
        elif tag == 'false':
                code_gen_expr([0, "Bool","new",(0,"Bool")]) # create the box object
                asm("li r2 <- 0") # value is 0 if false
                asm("st r1[1] <- r2")

        elif tag == 'minus': # operands are both Int values
                code_gen_expr(e[3]) # first operand object to r1
                asm("ld r2 <- r1[1]", "value from Int") # value from heap
                asm("push r2")
                code_gen_expr(e[4]) # second operand object to r1
                asm("pop r2")
                asm("ld r1 <- r1[1]", "value from Int") # value from heap
                asm("sub r2 <- r2 r1") # the subtract operation
                asm("push r2") # store value on the stack
                code_gen_expr([0,"Int","new",(0,"Int")]) # construct a new integer object
                asm("pop r2")
                asm("st r1[1] <- r2", "sub result in returned object") # put the value into the new object
        elif tag == 'times': # operands are both Int values
                code_gen_expr(e[3]) # first operand object to r1
                asm("ld r2 <- r1[1]", "value from Int") # value from heap
                asm("push r2")
                code_gen_expr(e[4]) # second operand object to r1
                asm("pop r2")
                asm("ld r1 <- r1[1]", "value from Int") # value from heap
                asm("mul r2 <- r2 r1") # the uml operation
                asm("push r2") # store value on the stack
                code_gen_expr([0,"Int","new",(0,"Int")]) # construct a new integer object
                asm("pop r2")
                asm("st r1[1] <- r2", "times result in returned object") # put the value into the new object
        elif tag == 'divide': # operands are both Int values
                code_gen_expr(e[3]) # first operand object to r1
                asm("ld r2 <- r1[1]", "value from Int") # value from heap
                asm("push r2")
                code_gen_expr(e[4]) # second operand object to r1
                asm("pop r2")
                asm("ld r1 <- r1[1]", "value from Int") # value from heap
                asm("div r2 <- r2 r1") # the div operation
                asm("push r2") # store value on the stack
                code_gen_expr([0,"Int","new",(0,"Int")]) # construct a new integer object
                asm("pop r2")
                asm("st r1[1] <- r2", "divide result in returned object") # put the value into the new object
        elif tag == 'negate': # operands are both Int values
                asm("li r2 <- 0")
                asm("push r2")
                code_gen_expr(e[3]) # second operand object to r1
                asm("pop r2")
                asm("ld r1 <- r1[1]", "value from Int")
                asm("sub r2 <- r2 r1") # the sub operation
                asm("push r2")
                code_gen_expr([0,"Int","new",(1,"Int")])
                asm("pop r2")
                asm("st r1[1] <- r2", "negate result stored in returned object")
        elif tag in ['le','lt','eq']: # operands are both Int values
                global ltiteration
                ltiteration += 1
                currentlt = ltiteration
                code_gen_expr(e[3]) # first operand object to r1
                asm("ld r2 <- r1[1]", "value from Int") # value from heap
                asm("push r2")
                code_gen_expr(e[4]) # second operand object to r1
                asm("pop r2")
                asm("ld r1 <- r1[1]", "value from Int") # value from heap
                asm("b" + tag + " r2 r1 truebool" + str(currentlt))
                asm("li r1 <- 0")
                asm("st r1[1] <- r2", "0 result in returned object")
                asm("truebool" + str(currentlt) + ":")
                asm("li r1 <- 1")
                asm("st r1[1] <- r1", "1 result in returned result")
        elif tag == 'if':
                global ifiteration
                ifiteration += 1
                currentif = ifiteration # in case of nested if statements
                code_gen_expr(e[3]) # 0 or 1 depending on whether Bool = true or false
                asm("ld r1 <- r1[1]", "value from Bool") # value from heap
                asm("bz r1 iffalse" + str(currentif))
                code_gen_expr(e[4]) # execute body if boolean is 1
                asm("jmp alldone" + str(currentif))
                asm("iffalse" + str(currentif) + ":")
                code_gen_expr(e[5]) # execute else if boolean is 0
                asm("alldone" + str(currentif) + ":")

        elif tag == 'not':
                global notiteration
                notiteration += 1
                currentnot = notiteration
                code_gen_expr(e[3]) #1 if true, 0 if false
                asm("ld r1 <- r1[1]", "value from Bool")
                asm("bz r1 ifzero" + str(currentnot))
                asm("li r2 <- 0")
                asm("st r1[1] <- r2") # if bool is not 0, it becomes 0
                asm("jmp finished" + str(currentnot)) # skip to end
                asm("ifzero" + str(currentnot) + ":")
                asm("li r2 <- 1")
                asm("st r1[1] <- r2") # if bool is 0, it becomes 1
                asm("finished" + str(currentnot) + ":")
                
		
#END OF ADDED TAGS-------------------------------------------------------------------------------------------------
        elif tag == 'block':
                for i in range(len(e[3])):
                        code_gen_expr(e[3][i])
        elif tag in ["self_dispatch","dynamic_dispatch","static_dispatch"]:
                typeexpr = code_gen_expr(e[3])
                asm("mov r7 <- r1")
                if tag == "self_dispatch":
                        try:
                                type = stab.find_symbol('SELF_TYPE')[1]
                        except:
                                type = None
                else:
                        if tag == "static_dispatch":
                                type = e[4]
                        else:
                                type = e[3][1]
                        if type == "SELF_TYPE":
                                type = stab.find_symbol('SELF_TYPE')[1]
                offset = 0
                for i, m in enumerate(ctab.all_methods(type)): # matches vtable
                        if m[0] == e[5][1]: # found matching method name
                                offset = i+2  # vtable offset for the method
                # push parameters onto stack
                for i, arg in enumerate(e[6]): 
                        code_gen_expr(arg)
                        asm("push r1")
                if typeexpr:
                        asm("mov r0 <- r7")
                asm("ld r2 <- r0[0]", "vtable for %s" % type)
                asm("ld r2 <- r2[%d]" % offset, "vtable offset for %s" % e[5][1])
                asm("push fp")
                asm("push r0")
                asm("call r2", type + "." + e[5][1])
                asm("pop r0")
                asm("pop fp")
                for i, arg in enumerate(e[6]): 
                        asm("pop r2")
        elif tag == "case":
                global casenum
                casenum = casenum + 1
                mycasenum = casenum
                caseexprval = code_gen_expr(e[3])
                asm("push r6")
                asm("mov r6 <- r1")
                #asm("b case%d..%s" % (mycasenum, "type")  # branch on the expression type name in real-time not compile-time
                caseelementtypes = []
                for elm in e[4]:
                        caseelementtypes.append(elm[1][1])
                for i, elm in enumerate(e[4]):
                        var = elm[0]
                        stab.add_symbol(var[1],"r6")
                        type = elm[1] # unused here except to set the label
                        asm("case%d..%s:" % (mycasenum, type[1]))
                        parent = ctab.get_parent(type[1])
                        while parent != "Object" and partent != None:
                                if parent not in caseelementtypes:
                                        asm("case%d..%s:" % (mycasenum, parent))
                                        caseelementtypes.append(parent)
                                parent = ctabe.get_parent(parent)
                        body = elm[2]
                        code_gen_expr(body)  # puts answer in r1
                        asm("b case%d..end" % mycasenum)

                asm("case%d..end:" % mycasenum)
                asm("pop r6")
                
        elif tag == "internal":
                if e[3] == 'IO.out_int':
                        asm("ld r1 <- fp[3]")
                        asm("ld r1 <- r1[1]")
                        asm("syscall IO.out_int")
                elif e[3] == 'IO.out_string':
                        asm("ld r1 <- fp[3]")
                        asm("ld r1 <- r1[1]")
                        asm("syscall IO.out_string")
                elif e[3] == 'IO.in_int':
                        asm("syscall IO.in_int")
                        asm("push r1")
                        code_gen_expr([0,"Int","new",(0,"Int")]) # construct a new integer object
                        asm("pop r2")
                        asm("st r1[1] <- r2", "int value in returned object") 
                elif e[3] == 'IO.in_string':
                        asm("syscall IO.in_string")
                        asm("push r1")
                        code_gen_expr([0,"String","new",(0,"String")]) # construct a new string object
                        asm("pop r2")
                        asm("st r1[1] <- r2", "string pointer in returned object")
                else:
                        print("internal method", e[3])
        else:
                print("ERROR: " + tag + " not implemented yet.")
                exit()
        #print("code_gen: " + tag, e[3:])
        #print("code_end: " + tag)


# constructor methods for all classes
for cname in sorted(ctab.all_classes()):
	asm("%s..new:" % cname, ";; constructor for %s" % cname)  # label for constructor
	# calling convention stuff"
	asm("mov fp <- sp")
	asm("push ra")
	# load size into a register (based on vtable pointer, attributes)
	asm("li r0 <- %d" % (1 + len(ctab.all_attributes(cname))))
	# ask OS for space on heap and put vtable and attributes in the space
	asm("alloc r0 r0")
	asm("la r1 <- %s..vtable" % cname)
	asm("st r0[0] <- r1")
	# for each attribute
	for i, a in enumerate(ctab.all_attributes(cname)):
		if a[1][1] == "unboxed":
			if cname == "String":
				asm("la r1 <- %s" % string_cache(""))
			else: # Int and Bool
				asm("li r1 <- 0")
		else:
			# call constructor for attribute

			if a[2]: # initializer
				asm(";; initializer expr w/ result in r1")
				code_gen_expr(a[2])  # maybe something should be on stab?
			else:
				asm("push fp")
				asm("push r0")
				asm("la r1 <- %s..new" % a[1][1]) # store location of heap object
				asm("call r1")
				asm("pop r0")
				asm("pop fp")
		asm("st r0[%d] <- r1" % (i+1))  # store the initialization value (or 0)
	asm("mov r1 <- r0")
	asm("pop ra")
	asm("return")


# other methods
for cname in ctab.all_classes():
	stab.enter_scope()  # entering a new class
	stab.add_symbol("self", "r0")	# r0 is always the object's heap address
	stab.add_symbol("SELF_TYPE", cname) # store the type name here for convenience
	for i, a in enumerate(ctab.all_attributes(cname)): # add class attributes
		stab.add_symbol(a[0][1], "r0[%d]" % (i+1)) # store address on heap

	for m in ctab.declared_methods(cname):
		stab.enter_scope()	# each method gets a new scope
		for i, p in enumerate(m[1]): # formal parameter list
			stab.add_symbol(p[0], "fp[%d]" % (i+3))  # parameters passed on stack

		asm("%s.%s:" % (cname, m[0]), ";; method definition")  # label for function def
		# calling convention stuff"
		asm("mov fp <- sp")
		asm("push ra")
		code_gen_expr(m[3]) # method body expression code
		asm("pop ra")
		asm("return")
		stab.clear_scope()

	stab.clear_scope()


# constants for the string literals
for i in string_table:
	asm(string_table[i] + ':', 'constant "' + i +'"')


# start: the wrapper program which calls the Main.main()
asm("start:")
asm("la r1 <- Main..new")
asm("call r1")  # create Main class
asm("la r1 <- Main.main")
asm("call r1")  # run the main method
asm("syscall exit")
	

f.close()
