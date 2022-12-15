import sys

# A framework for implementing A4

# API

# ast = read_AST(filename) # read in the .cl-ast file and recreate the tree
# 
# format_program(a) 
# ... etc to re-serialize the AST data
#
# AST Expression nodes always start with a line number, a type, and a tag
# The tag identifies the type of expresion (i.e. plus, let, if, etc.)
# The type field is initially set to None for all expressions.
# Other variant nodes (method, attribute, dispatch) will pad with None for optionals
#
#
# SymTab class - a simple symbol table (used when processing expressions)
#   add_symbol(name,data) # add a new symbol and data to associate with it
#	find_symbol(name) # returns the previously associated data (or None)
#	is_in_scope(name) # like find_symbol but only finds local variables
#	enter_scope()	# create a new scope for local variables
#	clear_scope()	# return to previous scope clearing all of the local variables
#
#
# ClassTab class - a class symbol table, generates serialized map of class data
#
#   add_class(name, parent_name)  # add a new class and its parent (or None)
#   get_class(name) # returns the class name or None if it isn't defined
#   get_parent(name) # returns the name of the parent class (or None)

#	all_classes() # returns a list of the all registered classes (including Object)
#   parent_map() # returns a string with the serialized parent_map

#   add_attribute(cname, aname, type, init) # add an attribute to a class
#   get_attribute(cname, aname) # returns the attribute defined in the class (or None)
#   find_attribute(cname, aname) # returns an attribute (possibility inherited) for the class (or None)

#   class_map() # returns a string with the serialized class_map (attribute map)

#   add_method(cname, mname, args, type, body) # add a method to a class
#   get_method(cname, mname) # returns the method defined in the class (or None)
#   find_method(cname, mname) # returns a method (possibility inherited) for the class (or None)

#   implementation_map() # returns a string with the serialized implementation_map




##### DESERIALIZE AST FILE

def read_AST(filename):

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
		tag = get_line()
		#print(line,tag)
		if tag in ['assign']:
			var = get_id()
			rhs = get_expr()
			return [line, None, tag, var, rhs]
		elif tag in ['dynamic_dispatch']:
			exp = get_expr()
			method = get_id()
			args = get_list(get_expr)
			return [line, None, tag, exp, None, method, args]
		elif tag in ['static_dispatch']:
			exp = get_expr()
			type = get_id()
			method = get_id()
			args = get_list(get_expr)
			return [line, None, tag, exp, type, method, args]
		elif tag in ['self_dispatch']:
			method = get_id()
			args = get_list(get_expr)
			return [line, None, tag, None, None, method, args]
		elif tag in ['if']:
			prd = get_expr()
			thn = get_expr()
			els = get_expr()
			return [line, None, tag, prd, thn, els]
		elif tag in ['block']:
			body = get_list(get_expr)
			return [line, None, tag, body]
		elif tag in ['new', 'identifier']:
			name = get_id()
			return [line, None, tag, name]
		elif tag in ['integer', 'string']:
			value = get_line()
			return [line, None, tag, value]
		elif tag in ['true', 'false']:
			return [line, None, tag]
		elif tag in ['negate', 'not', 'isvoid']:
			exp = get_expr()
			return [line, None, tag, exp]
		elif tag in ['while','plus','minus','times','divide','lt','le','eq']:
			exp1 = get_expr()
			exp2 = get_expr()
			return [line, None, tag, exp1, exp2]
		elif tag in ['let']:
			binding = get_list(get_let_binding)
			body = get_expr()
			return [line, None, tag, binding, body]
		elif tag in ['case']:
			exp = get_expr()
			elementslist = get_list(get_case_element)
			return [line, None, tag, exp, elementslist]
		else:
			print('Unrecognized expression', line, tag)
			exit()

	def get_let_binding():
		bind = get_line()
		var = get_id()
		type = get_id()
		if bind == 'let_binding_init':
			exp = get_expr()
			return (bind, var, type, exp)
		else:
			return (bind, var, type)

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

	# read_AST function body
	file = open(filename)
	program_classlist = get_list(get_class)
	file.close()
	return program_classlist



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
			x = self.get_attribute(name, i[0])
			if x == None:
				alist.append(i)
			else:
				alist.append(x)
				overrides[x] = True
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
				overrides[x] = True
		for m in self.data[name]['methods']:
			if m[0] in overrides: continue
			mlist.append(m)
		return mlist

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


'''
x = SymTab()
x.add_symbol("me", "Bool")
x.add_symbol("you", "Int")
print(x.data)
x.enter_scope()
x.add_symbol("them", "IO")
x.add_symbol("me", "String")
print(x.data)
print(x.find_symbol("me"))
print(x.find_symbol("you"))
print(x.is_in_scope("you"))
print(x.is_in_scope("me"))
x.clear_scope()
print(x.data)

print()
print()
'''

#t = ClassTab()
#print(t.parent_map())
#print(t.class_map())
#print()
#t.add_class("Main",None)
#t.add_attribute("Main",("2","x"),("2","Int"), ['2', None, 'integer', '2'])
#t.get_attribute("Main","x")[2][1] = 'Int'

#t.add_attribute("Main",("2","x"),("2","Int"), ('2', 'Int', 'integer', '2'))
#('2', 'Int','let', [('let_binding_init', ('2', 'a'), ('2', 'Int'), ('2', 'Int', 'integer', '4'))], ('2', 'Int', 'plus', ('2', 'Int', 'identifier', ('2', 'a')), ('2', 'Int', 'integer', '2'))))
#t.add_method("Main", 'main', [], ('3','Object'), ('4', 'Int', 'integer','13'))
#t.add_method("Main", 'extra', [('a','Int'),('b','Int')], ('5','Object'), 
#	('6', 'Int', 'plus', ('6', 'Int', 'identifier', ('6', 'a')), ('6', 'Int', 'identifier', ('6', 'b'))))
#print(t.class_map())
#t.add_class("Main2", "Main")
#print(t.parent_map())
#print()

#print(t.get_attribute("Main","a"))
#print(t.get_attribute("Main","b"))
#print()
#print(t.get_method("Main","main"))
#print(t.get_method("IO","out_int"))
#print(t.get_method("Main","out_int"))
#print(t.find_method("Main","out_int"))
#print("inherited---")
#print(t.inherited_methods("Main2"))
#print(t.inherited_methods("Main"))
#print(t.all_methods("Main"))
#print()
#print()


ast = read_AST('test.cl-ast')

ctab = ClassTab()

# Register the classes and their parents
for c in ast:
    name = c[0][1]
    parent = None
    if c[1] == 'inherits':
        parent = c[2][1]

    #can't inherit from these built-in classes
    if parent in ['Bool', 'Int', 'String']:
            print("ERROR: " + c[2][0] + " - Can't inherit from " + parent)
            exit()

    #can't have duplicate definitions
    if ctab.get_class(name):
            print("ERROR: " + c[0][0] + " - Class already exists: " + name)
            exit()

            
    ctab.add_class(name, parent)

# Verify the inheritance tree is a proper tree (i.e. no cycles) -- DONE
# and all parents are declared as classes -- DONE
# and no illegal inheritances (i.e no subclasses of Bool, Int, or String) -- DONE
# and no classes have duplicate definitions. -- DONE


#Check each class for inheritabce problems
for c in ctab.all_classes():
    p = ctab.get_parent(c)

    #all but Object must have a parent class that's declared
    if p: # for object
        if not ctab.get_class(p): #for everyone else
            print("ERROR " + c + " inheriting from non-existant " + p)
            exit()

    #make sure there's not a cycle and we can get to the root
    v = []
    while True:
        if p == None: #went through object to get here
            break
        elif p in v: #in loop, failure
            print("ERROR: recursive class definition for" + c + ': ', v)
            exit()
        else: #keep going
            v.append(p)
            p = ctab.get_parent(p)




# Output the .cl-type file

f = open('test.cl-type4','w')
f.write(ctab.class_map() + "\n")
f.write(ctab.implementation_map() + "\n")
f.write(ctab.parent_map() + "\n")
f.write(format_program(ast))
f.close()
