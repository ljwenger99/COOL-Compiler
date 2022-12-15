# C-- Compiler - starter code for the final exam - Charles Cooley 2020-10-13
#
# Things that need to be completed are marked with ToDo.
#
# I've tried to provide plenty of comments this time.
#
# There's no class table, but this time there are three symbol tables.
#       One table holds the type of a variable (or return type of a function).
#       One table holds the argument type list for functions.
#       One table holds the address (or offset) for functions and variables.
#               Functions and global variables use their label as an address.
#               Paramters and local variables use offset numbers from the FP.
#               (I wrote the code dealing with the ugliness of the addresses).



#LUCAS WENGER
#NOTE TO CHARLES!!!!!!!!!: QUESTIONS ANSWERED WITH COMMENTS AT BOTTOM


import sys

filename = "basic"

f = open(filename + ".cmm")
data = f.readlines()
data = "".join(data)
f.close()

f = open(filename + '.cl-asm','w')

############ Helper routines

# ToDo: optional but fairly easy enhancement to optimize the code
#       Have asm hold any "push r1" instruction until it receives the next instruction
#       if the next instruction is "pop r1" ignore both
#       if not output both the "push r1" and whatever follows
#       (Yes this is a dirty hack, but eliminates a very common problem.)

# ToDo: some other suggested optional enhancements
#       (DONE)Use minus for the unary minus instead of tilde (it's actually pretty easy)
#       Add built-in len and substr functions (there are String system calls).
#       Add an official bool type (still an int, but unique type checking)
#       Add a simple if construct (and maybe while to go with it)
#       (DONE) Make the semicolon just before a } optional. (It's just a change to the grammar.)


# output format asm code to the .cl-asm file
def asm(instr, comment = ""):
        if instr[-1] == ":": # label
                if len(comment) > 0 and comment[0] == ';':
                        f.write("%24s;; ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;\n" % "");
                f.write("%-24s%s\n" % (instr, comment))
        elif comment:
                f.write("%24s%s\t;; %s\n" % ("",instr,comment))
        else:
                f.write("%24s%s\n" % ("",instr))

# store from r1 into a variable in memory, pass the variable name only
def asmStoreTo(sym):
        addr = symAddr.find_symbol(sym)
        if isinstance(addr, int):
                asm("st fp[%d] <- r1" % addr)
        else:
                asm("la r0 <- %s" % addr)
                asm("st r0[0] <- r1")

# load from a variable in memory into r1, pass the variable name only
def asmLoadFrom(sym):
        addr = symAddr.find_symbol(sym)
        if isinstance(addr, int):
                asm("ld r1 <- fp[%d]" % addr)
        else:
                asm("la r0 <- %s" % addr)
                asm("ld r1 <- r0[0]")

# quick print a message and quit
def error(message, line = 0):
        print("ERROR: %s (line %d)" % (message, line))
        exit()


######## SymbolTable (there will be more than one instance this time)
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
                                return d
                return None

        def is_in_scope(self, name):
                for (n,d) in reversed(self.data):
                        if n == name:
                                return d
                        if n == "SCOPE":
                                return None
                return None



# Cache for string literals
class StringCache():
        def __init__(self):
                self.table = {}
                self.count = 0
        def string(self, value):
                if not value in self.table:
                        self.table[value] = "string" + str(self.count)
                        self.count = self.count + 1
                return self.table[value]
        def items(self):
                return self.table.items()




######## LEXER

from cdcLexer import Lexer, LexToken

def StartComment(d,t):
        return 'COMMENT'

def EndComment(d,t):
        return 'INITIAL'

def FinishState(d):
        if d._state == 'INITIAL':
                return 'DONE', 'Scan successful'
        return 'INITIAL'

def StartString(d,t):
        d.string_text = ''
        d.string_start_line = t.line
        d.string_start_pos = t.pos
        return 'STRING'

def BuildString(d,t):
        d.string_text += t.value
        return 'STRING'

def EndString(d,t):
        t.value = d.string_text
        t.line = d.string_start_line
        t.pos = d.string_start_pos
        return 'INITIAL', t

mylexer = Lexer('INITIAL', FinishState, 
        {"INITIAL" : [
                ('WHITESPACE', r'[ \t\n]+', 'IGNORE'),
                ('COMMENTSTART', r'\/\*', StartComment),
                ('SEMI', r'(\;)'),
                ('LPAREN', r'(\()'),
                ('RPAREN', r'(\))'),
                ('LBRACE', r'(\{)'),
                ('RBRACE', r'(\})'),
                ('PLUS', r'(\+)'),
                ('MINUS', r'(\-)'),
                ('TIMES', r'(\*)'),
                ('DIVIDE', r'(\/)'),
                ('INTEGER', r'(\d+)'),
               # ('NEGATE', r'(\~)'),
                ('COMMA', r'(\,)'),
                ('ASSIGN',r'(\=)'),
                ('RETURN',r'((?i:return)\b)'),
                ('PRINT',r'((?i:print)\b)'),
                ('READ',r'((?i:read)\b)'),
                ('STRINGSTART',r'(\")', StartString),
                ('TYPE', r'(void|int|str)'),
                ('ID', r'([a-zA-Z_]\w*)')],
        # (DONE)ToDo: Add the missing tokens including strings ##NOT NECESSARILY HERE EXACTLY
        "COMMENT" : [
                ('COMMENTEND', r'\*\/', EndComment),
                ('COMMENTTEXT', r'(.|\n)', 'IGNORE')],
        "STRING" : [
                ('STRING', r'(\")', EndString),
                ('STRINGTEXT', r'(.|\n)', BuildString)]})



######## PARSER with type checking and code generation (single pass)

symType = SymTab()  # stores the type for both variables and functions
symAddr = SymTab()      # stores the address (or offset) for variables and functions
symArgs = SymTab()      # stores the formal parameter types for functions

cache = StringCache() # all literal strings must use the cache to be assigned an address


from ply.yacc import yacc

tokens = ( # complete token list
        'PLUS',
        'MINUS',
        'TIMES',
        'DIVIDE',
        'INTEGER',
      #  'NEGATE',
        'STRING',
        'ID',
        'TYPE',
        'LPAREN',
        'RPAREN',
        'LBRACE',
        'RBRACE',
        'SEMI',
        'COMMA',
        'ASSIGN',
        'RETURN',
        'PRINT',
        'READ',
        'DONE')

precedence = (
    ('left','PLUS','MINUS'),
    ('left','TIMES','DIVIDE'),
    #('right','NEGATE'),
    )


# A C-- program 
#       Programs consist of an arbitrary list of global variable and function declarations.
#       The declarations must be processed from left to right (top to bottom) of the code.
#       Variable and function declarations can be intermixed, variables don't have to be first.
#       Every program must have a void main() function declared. (In practice it will be last.)
#       DONE is a special marker provided at the end of the stream of tokens.
#       When the program is validated the string cache and bootstrap code can be generated.

# program ::= declaration { declaration } DONE
def p_program(p):
        '''program : declarations DONE'''

        # (DONE) ToDo: check for a valid main function
        if symType.find_symbol('main') != 'void':#if main function is not in symType or is not type void
                error("No valid main method")
        # generate the string cache and initializer code
        for (string,label) in cache.items(): 
                asm(label + ':', 'constant "' + string + '"')
        asm("start:")
        asm("la r1 <- Function.main")
        asm("call r1")  # run the main method
        asm("syscall exit")


def p_declarations(p):  # recursion on the left to ensure the left is processed first!
        '''declarations : declarations declaration
                        | declaration'''
        pass # nothing needs to be done, just make sure the declarations are run in order

# declaration ::= vardecl | funcdecl
def p_declaration(p):
        '''declaration : gvardecl 
                        | funcdecl'''
        pass  # the real work is done below, but this lets you alternate between them



# Global variables
#       They can't be void, re-declared, or initialized with the wrong type of literal.
#       The only initializers allowed are literal values (no expressions here).
#       Ints can be stored directly as a constant at a memory location.
#       Strs must be cached in the string table and their address stored as a constant.
#       Global variables are addressed by their label addresses.
#       While the assembly code generates them as "constant" that's just a way to allocate
#               memory for the life of the program and doesn't mean the values can't change.

# gvardecl ::= TYPE ID [ "=" ( INTEGER | STRING ) ] ";" 
def p_gvardecl(p):
        '''gvardecl : TYPE ID gvarinit'''
        
        # (DONE)ToDo: various error checks, add to type symbol table
        if p[1] not in ['str','int']: #makes sure type is int or str
                error('Not a valid type')
        if symType.find_symbol(p[2]): #makes sure variable is not already redeclared
                error('Cannot redeclare variables')
        if p[3][1]: #if there is an initializer
                if p[3][1] != p[1]: #if the initializer type does not equal the declared type
                        error('Initializer type does not match stated type')
        #code below ensures initializer is either a string or integer literal,
        #so we can go ahead and put it in the table
        symType.add_symbol(p[2], p[1]) #add symbol to table
        # all is well, so ...
        val = cache.string("")  # assume an uninitialized string
        if p[1] == 'str' and p[3][1] == 'str':
                val = cache.string(p[3][0])     # found an initializer string
        if p[1] == 'int':
                val = p[3][0]  # initializer value for int (or 0 if not initialized)
        asm("GlobalVar.%s:" % p[2], "constant %s" % val) # store it in memory
        symAddr.add_symbol(p[2], "GlobalVar.%s" % p[2])  # add location to addr symbol table

def     p_gvarinit_none(p):
        '''gvarinit : SEMI'''
        p[0] = (0, None)  # no type when no initializer but default value to 0

def     p_gvarinit_int(p):
        '''gvarinit : ASSIGN INTEGER SEMI'''
        p[0] = (p[2], 'int')  # int value type

def     p_gvarinit_str(p):
        '''gvarinit : ASSIGN STRING SEMI'''
        p[0] = (p[2], 'str')  # str value type


# Functions
#       Function names are in the same namespace as variables.
#       Functions can be declared was void and can have any number of parameters.
#       There are four important stages in processing function definitions.
#       On seeing the function name and type:
#               Functions start a new scope for local variables.
#               (That means enter scope for the type and addr symbol tables.
#               A dummy "return-type" entry on the type symbol table is used to check return type.
#               A dummy "local-count" entry on the addr symbol table can track local variable use.
#               Initial code for moving the FP and storing the RA can be generated.
#               p[0] will be a tuple with the type and name of the function.
#       On processing the parameter list:
#               Paramters can't be of type void and names can't be reused in the same scope.
#               FP offset entries are added to the addr symbol table for each parameter.
#               (The values are based on where arguments will be pushed when the function is called.)
#               p[0] returns a list of the types (and only types) of the paramters (in order).
#       On processing the body of the function:
#               Code will be generated based on the symbol table entries.
#               All statements except a return will set p[0] to 'void'.
#               A return statement will set p[0] to the expression type.
#               The body rule will forward the return type up to the main declaration.
#       On returning to the main funcdecl rule:
#               The types of the parameters (in order) must be stored in the args symbol table.
#               (The args table holds parameters for type checking when functions are called.)
#               (Storing the list is done here because we need both that list and the function name.)
#               The actual returned type needs to be checked against the function type (again).
#               Any local variables have to be popped from the stack. (Using the local-count entry).
#               The type and addr symbol table scope can be cleared.
#               Code is generated to restore the RA and return from the function.

#funcdecl ::= TYPE ID "(" [ TYPE ID { "," TYPE ID } ] ")" block
def p_funcdecl(p):
        '''funcdecl : funcname LPAREN paramlist RPAREN block'''
        # The three parts must be processed in order, so funcname is a sub-rule
        (functype, funcname) = p[1]
        paramtypelist = p[3]
        returntype = p[5]

        # (DONE)ToDo: deal with arguments (main doesn't have any) and check return type
        symArgs.add_symbol(funcname, paramtypelist) #Add to args table entry with function name and parameter type list

        if returntype != functype or returntype != symType.find_symbol("return-type"): #not sure why we have return-type and functype -- aren't they the same thing?
                error("Declared return type " + functype + " does not match actual return type " + returntype)

#Not in the todo, but it looks like this is needed based on comment above------------
                
        count = symAddr.is_in_scope("local-count")
        for local in range(count[0]):
                asm("pop r2")

        symType.clear_scope()
        symAddr.clear_scope()

#------------------------------------------------------------------------------------
        
        asm("pop ra") # return from the function
        asm("return")

def p_funcname(p):
        '''funcname : TYPE ID'''
        # any type is valid for functions

        # (DONE)ToDo: check for redeclaration of name, add to type symbol table
        if symType.find_symbol(p[2]):
                error('Function name already declared')
        symType.add_symbol(p[2], p[1])

        asm("Function.%s:" % p[2])
        symAddr.add_symbol(p[2],"Function.%s" % p[2]) # add function location at global scope
        symType.enter_scope()  # enter a new scope before processing the parameters
        symAddr.enter_scope()
        symType.add_symbol("return-type", p[1]) # so return statement can check validity
        symAddr.add_symbol("local-count", [0]) # track local variable declarations with a hack

        asm("mov fp <- sp")  # start the function body definition
        asm("push ra")
        p[0] = (p[1],p[2])  # return the function type and name

def p_paramlist_none(p):
        '''paramlist : '''
        p[0] = []

def p_paramlist_some(p):
        '''paramlist : params'''
        p[0] = p[1]

def p_params_one(p):
        '''params : TYPE ID'''
        if p[1] == 'void':
                error("Parameter can't be declared as void %s" % p[2])
        if symType.is_in_scope(p[2]):
                error("Redeclaration of parameter %s" % p[2])
        symType.add_symbol(p[2],p[1])  # need to record type and location
        symAddr.add_symbol(p[2],(2))  # just the offset from the fp as a number (first is at 2)
        p[0] = [p[1]]  # only types are needed for typechecking at function call

def p_params_some(p):
        '''params : TYPE ID COMMA params'''
        # (DONE)ToDo: fix this based on p_params_one logic
        if p[1] == 'void':
                error("Parameter can't be declared as void %s" % p[2])
        if symType.is_in_scope(p[2]):
                error("Redeclaration of parameter %s" % p[2])
        symType.add_symbol(p[2],p[1])  # need to record type and location
        symAddr.add_symbol(p[2],(2))  # just the offset from the fp as a number (first is at 2)
        p[0] = [p[1]] + p[4]



# block ::= "{" { stmt ";" } "}"
def p_block(p):
        '''block : LBRACE stmtlist RBRACE'''
        p[0] = p[2]  # return type from the statment list

def p_stmtlist_none(p):
        '''stmtlist : '''
        p[0] = 'void'  # no return statement

def p_stmtlist_some(p):
        '''stmtlist : stmtlist stmt SEMI'''
        if p[2] != 'void':
                p[0] = p[2]
        else:
                p[0] = p[1]


#This works if we know that stmtlist_some goes first, if applicable.
#Tested, and it seems to work! 
def p_stmtlist_last(p):
        '''stmtlist : stmtlist stmt'''
        if p[2] != 'void':
                p[0] = p[2]
        else:
                p[0] = p[1]


# Statements
#       All statements except return set p[0] to 'void'.
#       The return sets p[0] to the expression type being returned.
#       The result of all expressions will be on the stack.
#       (Storing results on the stack isn't efficient but it is easy.)
#       Expression results will need to be removed from the stack for statements like return.
#       Statements are not expressions and do not push anything onto the stack.
#       The print and read statements are wrappers for IO syscalls.
#       Local variables are simply pushed onto the stack.
#       Local variables are reference with a negative offset from the FP.
#       The local-count must be updated so the local variables can be popped off the stack later.
#       A function call can be a statement, but only for functions with a void type.


# stmt ::= "print" "(" expr ")"
def p_stmt_print(p):
        '''stmt : PRINT LPAREN expr RPAREN'''
        # (DONE)ToDo: call the correct IO system calls
        if p[3] == 'int':
                asm("syscall IO.out_int")
        elif p[3] == "str":
                asm("syscall IO.out_string")
        asm("pop r1") # the return value from the expression, type is in p[3]
        p[0] = 'void' # not a return


# stmt ::= "read" "(" ID ")"
def p_stmt_read(p):
        '''stmt : READ LPAREN ID RPAREN'''
        type = symType.find_symbol(p[3])
        if type == 'int':
                asm("syscall IO.in_int")
        elif type == "str":
                asm("syscall IO.in_string")
        asmStoreTo(p[3])
        p[0] = 'void' # not a return


# stmt ::= TYPE ID [ "=" expr ]
def p_stmt_vardecl_noinit(p):
        '''stmt : TYPE ID'''
        if p[1] == 'void':
                error("Variable can't be declared as void %s" % p[2])
        if symType.is_in_scope(p[2]):
                error("Redeclaration of variable %s" % p[2])
        count = symAddr.is_in_scope("local-count")
        count[0] = count[0] + 1  # hack to track offset of each local variable
        symType.add_symbol(p[2],p[1])
        symAddr.add_symbol(p[2], 0 - count[0])
        if p[1] == 'str':
                asm("la r1 <- %s" % cache.string(""))
        else:
                asm("li r1 <- 0")
        asm("push r1") 
        p[0] = 'void' # not a return


def p_stmt_vardecl_init(p):
        '''stmt : TYPE ID ASSIGN expr'''
        # (DONE)ToDo: similar to the noinit version, but the expr value is already on the stack!
        if p[1] == 'void':
                error("Variable can't be declared as void %s" % p[2])
        if symType.is_in_scope(p[2]):
                error("Redeclaration of variable %s" % p[2])
        count = symAddr.is_in_scope("local-count")
        count[0] = count[0] + 1  # hack to track offset of each local variable
        symType.add_symbol(p[2],p[1])
        symAddr.add_symbol(p[2], 0 - count[0])
        #expr already on the stack!
        p[0] = 'void' # not a return
                
        
# stmt ::= "return" expr
def p_stmt_return(p):
        '''stmt : RETURN expr'''
        asm("pop r1")
        p[0] = p[2]

# stmt ::= ID "=" expr
def p_stmt_assign(p):
        '''stmt : ID ASSIGN expr'''
        # (DONE)ToDo: check declaration of ID
        if not symType.find_symbol(p[1]):
                error("ID not yet declared")
        # (DONE)ToDo: match ID and expr types
        #Does this mean ID type is implied in expr type, and we should store it in table?
        symType.add_symbol(p[1],p[3])
        asm("pop r1")
        asmStoreTo(p[1])
        p[0] = 'void' # not a return


# stmt ::= call
def p_stmt_call(p):
        '''stmt : call'''
        # (DONE)ToDo: should be straight forward enough, need to check type
        if p[1] != 'void':
                error("Call as a statement must be void type")
        p[0] = p[1]
                




# Expressions
#       All expressions must store their result on the stack.
#       (Storing results on the stack isn't efficient but it is easy.)
#       (In many cases the result will be pushed on the stack then popped back immediately.)
#       For integer literals, use the immediate literal value.
#       For string literals, use the address returned from cache.string.
#       For variables, use the asmLoadFrom() function to fill r1 with the currect value.
#       Using the stack means, the arithmetic operators are easy. (pop,pop,operation,push)
#       A function call is a valid expression only if it returns an int or str type.


# expr ::= INTEGER | STRING | ID
def p_expr_int(p):
        '''expr : INTEGER'''
        # (DONE)ToDo: use an "li"
        asm("li r1 <- " + str(p[1]))
        asm("push r1")
        p[0] = 'int'

def p_expr_str(p):
        '''expr : STRING'''
        # (DONE)ToDo: use ane "la" and the string cache
        asm("la r1 <- %s" % cache.string(p[1]))
        asm("push r1")
        p[0] = 'str'

def p_expr_var(p):
        '''expr : ID'''
        type = symType.find_symbol(p[1])
        if type == None:
                error("Variable undeclared: %s" % p[1])
        asmLoadFrom(p[1])
        asm("push r1")
        p[0] = type

# expr ::= expr "+" expr
def p_expr_plus(p):
        '''expr : expr PLUS expr'''
        if p[1] == 'str' and p[3] == 'str':
                asm("pop r2")
                asm("pop r1")
                asm("syscall String.concat")
                asm("push r1")
                p[0] = 'str'
        # (DONE)ToDo: add code for adding integers
        elif p[1] == 'int' and p[3] == 'int':
                asm("pop r2")
                asm("pop r1")
                asm("add r1 <- r1 r2")
                asm("push r1")
                p[0] = 'int'
        else:
                error("Attempt to add invalid types")
        
# expr ::= expr "-" expr
def p_expr_minus(p):
        '''expr : expr MINUS expr'''
        # (DONE)ToDo: easy
        if p[1] == 'int' and p[3] == 'int':
                asm("pop r2")
                asm("pop r1")
                asm("sub r1 <- r1 r2")
                asm("push r1")
                p[0] = 'int'
        else:
                error("Attempt to add invalid types")

# expr ::= expr "*" expr
def p_expr_times(p):
        '''expr : expr TIMES expr'''
        # (DONE)ToDo: easy
        if p[1] == 'int' and p[3] == 'int':
                asm("pop r2")
                asm("pop r1")
                asm("mul r1 <- r1 r2")
                asm("push r1")
                p[0] = 'int'
        else:
                error("Attempt to add invalid types")

# expr ::= expr "/" expr
def p_expr_divide(p):
        '''expr : expr DIVIDE expr'''
        # (DONE)ToDo: easy
        if p[1] == 'int' and p[3] == 'int':
                asm("pop r2")
                asm("pop r1")
                asm("div r1 <- r1 r2")
                asm("push r1")
                p[0] = 'int'
        else:
                error("Attempt to add invalid types")

# expr ::= "~" expr
def p_expr_negate(p):
        '''expr : MINUS expr'''
        # (DONE)ToDo: subtract from 0
        if p[2] == 'int':
                asm("pop r2")
                asm("li r1 <- 0")
                asm("sub r1 <- r1 r2")
                asm("push r1")
                p[0] = 'int'
        else:
                error("Only an int can be negated")


# expr ::= call
def p_expr_call(p):
        '''expr : call'''
        if p[1] == 'void':
                error("Can't use void functions in expressions")
        asm("push r1")  # not void so push the result like all expressions
        p[0] = p[1]



# Function Calls
#       Function names are in the global scope.
#       The address of the function can be found in the addr symbol table.
#       Argument expressions get pushed on the stack automatically as they are evaluated.
#       (The order of evaluation of the expressions does matter.)
#       The arguments must be popped back off after the call returns.
#       A list of the expression types should be returned in p[0].
#       The expression types must match the declared types for the function (args symbol table).
#       The p[0] value should be set to the function's return type (from the type symbol table).
#       Expressions and statments will use the p[0] result to decide if the call was legal.

# call ::= ID "(" [ expr { "," expr } ] ")" 
def p_function_call(p):
        '''call ::= ID LPAREN arglist RPAREN'''
        addr = symAddr.find_symbol(p[1])
        if addr == None:
                error("Function not defined: %s" % p[1])
        # (DONE)ToDo: verify all of the argument types against the parameter list in symArgs
        if not p[3] == symArgs.find_symbol(p[1]):
                error("Argument(s) declared do not match arguments expected")
        
        asm("la r1 <- %s" % addr)
        asm("push fp")
        asm("call r1")
        asm("pop fp")
        for i, arg in enumerate(p[3]): 
                asm("pop r2")
        p[0] = symType.find_symbol(p[1])
        

def p_arglist_none(p):
        '''arglist : '''
        p[0] = []

def p_arglist_some(p):
        '''arglist : args'''
        p[0] = p[1]

def p_args_one(p):
        '''args : expr'''
        asm("; argument") # expression already pushed it on the stack
        p[0] = [p[1]] # bubble the type up

def p_args_some(p):
        '''args : args COMMA expr'''
        asm("; argument") # expression already pushed it on the stack
        p[0] = p[1] + [p[3]]  # only types are needed for typechecking at function call




def p_error(p):
        error(p)

mylexer.load(data)

yacc().parse(lexer = mylexer)


f.close()

#QUESTION ONE
#Data for a program can be stored in four different places, the registers, the stack, the heap, and the static data
#region. Identify the advantages and disadvantages of each type of storage. How and why are each of the four used
#in storing various types of variables?

####THE HEAP####
#The heap is typically used to store dynamically created variables. In this case, our global variables are an example
#of something that would be stored in the heap. Typically the operating system manages this place in the memory.
#I have not taken data structures, so I can only talk about what we learned in class and how it relates to this
#program. One advantage/disadvantage is that the heap is used to manage global memory. This is useful, but can be
#more complicated. A disadvantage is that it is slower than some of the other places to store things in. An advantage
#is that it is more flexible. Memory can be allocated and removed in any order. 
####THE REGISTERS####
#The registers are sort of a set of pockets where data can be stored. We used them often to store data we were
#working with in the moment and manipulating before putting it back on the stack to be used by something else. A
#disadvantage would be that the registers must be specifically assigned, as opposed to the stack, where you can pile
#things on top without worrying about accidentally overwriting any data. An advantage is that you can access any
#register at any time, as opposed to the heap, where you can only access what's on top. The registers have to be
#manually assigned by assembly code. The registers would be used for similar things as the stack (local variables,
#integers, strings, etc.), but you would typically keep things here if you are working with or manipulating them. 
####THE STACK####
#Oh boy, is the stack great. This is a quick and easy place to store data without worrying about overwriting
#anything. It is usually used to store local variabls and other values (int, str, etc.), especially ones that may
#change as you work with functions and manipulate the registers. There is a stack pointer that always points to the
#top of the stack and a frame pointer that points to any location in the stack. An advantage is that it keeps data
#safe with little worry of overwriting any data. A disadvantage is that it is more difficult to access than the
#registers. We often stored data from registers on the stack to either transfer them between functions or to keep them
#safe while using functions. 
####STATIC DATA REGION####
#This is the foundation. The solid rock of our code. The cornerstone. It consists of the executable code, constants,
#and potentially space for global variables. The basic data types (boolean, int, str) are stored here. This is
#essentially the place to store data that will not change throughout the program. An advantage is just that: it keeps
#data safe from change. A disadvantage is that it is more complicated and more difficult to change. 

#QUESTION TWO
#Small changes to grammar rules can have a large impact. If you replace 'stmtlist : stmtlist stmt SEMI' as used in
#the C-- implementation with the similar 'stmtlist : stmt SEMI stmtlist' (and change the p[0] rules appropriately)
#what changes about how the program is interpreted?

####ANSWER####
#First off, it looks like they would both end in a semicolon, assuming that stmtlist could be empty. It also looks
#like the first one would add statements to the end of the statement list, whereas the first one would add them to
#the beginning, if you were adding the lists in order. But, we are not adding lists in our code. Still, it would
#have an effect. Since you could translate the appropriate p statements, the code would practically still work,
#but its inner mechanisms would be altered. I tested it and didn't get any differences in the asm code, but
#theoretically, if the one on the right is processed first, the asm should generate the code for the last instruction
#before the first one. Credit to Charles Cooley for that massive last hint/answer. 
