#Lucas Wenger
#Assignment 3 -- Parser
#Worked some with Tessa and Silas

#Read in file from Assignment2--DONE
#Deserialize file into tokens--DONE
#Feed tokens to PLY Lexer Format--DONE
#Define AST Representation -- DONE
#Define PA3 Parser as Grammar Rules -- DONE
#Serialize AST (print it out) -- DONE

import sys
from ply.lex import LexToken
import ply.yacc as yacc #the PLY parser


tokens_filename = sys.argv[1] #FOR FINISHED PRODUCT
#tokens_filename = input("Enter a file name:\n") #FOR TESTING
f = open(tokens_filename,'r')
tokens_lines = f.readlines()
f.close()


def get_token_line():
    global tokens_lines
    result = tokens_lines[0].strip()
    tokens_lines = tokens_lines[1:]
    return result

pa2_tokens = []

while tokens_lines != []:
    line_number = get_token_line()
    token_type = get_token_line()
    if token_type in ['identifier', 'integer', 'type', 'string']:
        token_lexeme = get_token_line()
    else:
        token_lexeme = token_type
    pa2_tokens += [(line_number, token_type.upper(), token_lexeme)]

#Use PA2 Tokens as Lexer
class PA2Lexer(object):
    def token(whatever):
        global pa2_tokens
        if pa2_tokens == []:
            return None
        (line, token_type, lexeme) = pa2_tokens[0]
        pa2_tokens = pa2_tokens[1:]
        tok = LexToken
        tok.type = token_type
        tok.value = lexeme
        tok.lineno = line
        tok.lexpos = 0
        return tok

pa2lexer = PA2Lexer()

#Define PA3 Parser

tokens = (
    'LBRACE', 
    'RBRACE', 
    'LPAREN', 
    'RPAREN', 
    'INTEGER',
    'CLASS',
    'ELSE', 
    'FALSE', 
    'FI', 
    'IF', 
    'IN',
    'INHERITS', 
    'ISVOID', 
    'LET', 
    'LOOP', 
    'POOL', 
    'THEN', 
    'WHILE', 
    'CASE', 
    'ESAC', 
    'NEW', 
    'OF', 
    'NOT', 
    'TRUE', 
    'AT', 
    'ADD', 
    'SUBTRACT',
    'MULTIPLY', 
    'DIVIDE', 
    'RARROW', 
    'LARROW',
    'LE', 
    'LT', 
    'EQUAL', 
    'COLON', 
    'COMMA',
    'SEMI',
    'TILDE',
    'DOT',
    'IDENTIFIER',
    'TYPE', 
    'STRING'
    )

precedence = (  #NOT SURE IF COMMENTED ONES ARE CORRECT -- TAKEN FROM PRECEDENCE RULES IN COOL DOCUMENTATION
    ('left', 'DOT'),
    ('left', 'AT'),
    ('right', 'TILDE'),
    ('left', 'ISVOID'),
    ('left', 'ADD', 'SUBTRACT'),
    ('left', 'MULTIPLY', 'DIVIDE'),
    ('left', 'LE', 'LT', 'EQUAL'),
    ('left', 'NOT'),
    ('right', 'LARROW') #binds more tightly 
    )

#GRAMMAR RULES

#PROGRAM -- done

def p_program_classlist(p): 
    'program : classlist'
    p[0] = p[1]

#CLASS -- done

def p_classlist_one(p): 
    'classlist : class SEMI'
    p[0] = [p[1]]

def p_classlist_some(p):
    'classlist : class SEMI classlist'
    p[0] = [p[1]] + p[3]

def p_class_noinherit(p):
    'class : CLASS type LBRACE featurelist RBRACE'
    p[0] = (p.lineno(1), 'class_noinherit', p[2], p[4])

def p_class_inherit(p):
    'class : CLASS type INHERITS type LBRACE featurelist RBRACE'
    p[0] = (p.lineno(1), 'class_inherit', p[2], p[4], p[6])

#TYPE -- done

def p_type(p):
    'type : TYPE'
    p[0] = (p.lineno(1), p[1])

#IDENTIFIER -- done

def p_identifier(p):
    'identifier : IDENTIFIER'
    p[0] = (p.lineno(1), p[1])

#FORMAL -- done

def p_formallist_some(p):
    'formallist : formal COMMA formallist'
    p[0] = [p[1]] + p[3]

def p_formallist_one(p):
    'formallist : formal'
    p[0] = [p[1]]

def p_formal(p):
    'formal : identifier COLON type'
    p[0] = (p[1][0], p[1], p[3])

#FEATURE -- done

def p_featurelist_none(p):
    'featurelist : '
    p[0] = []

def p_featurelist_some(p):
    'featurelist : feature SEMI featurelist'
    p[0] = [p[1]] + p[3]

def p_feature_attribute(p):
    'feature : attribute'
    p[0] = p[1]

def p_attributenoinit(p):
    'attribute : identifier COLON type'
    p[0] = (p[1][0], 'attribute_no_init', p[1], p[3])

def p_attributeinit(p):
    'attribute : identifier COLON type LARROW exp' 
    p[0] = (p[1][0], 'attribute_init', p[1], p[3], p[5])

def p_feature_method_withformals(p): 
    'feature : identifier LPAREN formallist RPAREN COLON type LBRACE exp RBRACE'
    p[0] = (p[1][0], 'method', p[1], p[3], p[6], p[8])

def p_feature_method_noformals(p): 
    'feature : identifier LPAREN RPAREN COLON type LBRACE exp RBRACE'
    p[0] = (p[1][0], 'method', p[1], [], p[5], p[7])

#EXPRESSION -- done

def p_explist_semi_one(p):
    'explist_semi : exp SEMI'
    p[0] = [p[1]]

def p_explist_semi_some(p): 
    'explist_semi : exp SEMI explist_semi'
    p[0] = [p[1]] + p[3]

def p_explist_comma_one(p):
    'explist_comma : exp'
    p[0] = [p[1]]

def p_explist_comma_some(p):
    'explist_comma : exp COMMA explist_comma'
    p[0] = [p[2]] + p[3]

def p_exp_assign(p):
    'exp : identifier LARROW exp'
    p[0] = (p[1][0], 'assign', p[1], p[3])

def p_exp_dynamicdispatch_withexp(p):
    'exp : exp DOT identifier LPAREN explist_comma RPAREN'
    p[0] = (p[1][0], 'dynamic_dispatch', p[1], p[3], p[5])

def p_exp_dynamicdispatch_noexp(p):
    'exp : exp DOT identifier LPAREN RPAREN'
    p[0] = (p[1][0], 'dynamic_dispatch', p[1], p[3], [])

def p_exp_staticdispatch_withexp(p):
    'exp : exp AT type DOT identifier LPAREN explist_comma RPAREN'
    p[0] = (p[1][0], 'static_dispatch', p[1], p[3], p[5], p[7])

def p_exp_staticdispatch_noexp(p):
    'exp : exp AT type DOT identifier LPAREN RPAREN'
    p[0] = (p[1][0], 'static_dispatch', p[1], p[3], p[5], [])

def p_exp_selfdispatch_withexp(p): 
    'exp : identifier LPAREN explist_comma RPAREN'
    p[0] = (p[1][0], 'self_dispatch', p[1], p[3])

def p_exp_selfdispatch_noexp(p): 
    'exp : identifier LPAREN RPAREN'
    p[0] = (p[1][0], 'self_dispatch', p[1], [])

def p_exp_if(p):
    'exp : IF exp THEN exp ELSE exp FI'
    p[0] = (p.lineno(1), 'if', p[2], p[4], p[6])

def p_exp_while(p):
    'exp : WHILE exp LOOP exp POOL'
    p[0] = (p.lineno(1), 'while', p[2], p[4])

def p_exp_block(p):
    'exp : LBRACE explist_semi RBRACE'
    p[0] = (p.lineno(1), 'block', p[2])

def p_exp_new(p):
    'exp : NEW type'
    p[0] = (p.lineno(1), 'new', p[2])

def p_exp_isvoid(p):
    'exp : ISVOID exp'
    p[0] = (p.lineno(1), 'isvoid', p[2])

def p_exp_plus(p):
    'exp : exp ADD exp'
    p[0] = (p[1][0], 'plus', p[1], p[3])

def p_exp_minus(p):
    'exp : exp SUBTRACT exp'
    p[0] = (p[1][0], 'minus', p[1], p[3])

def p_exp_times(p):
    'exp : exp MULTIPLY exp'
    p[0] = (p[1][0], 'multiply', p[1], p[3])

def p_exp_divide(p):
    'exp : exp DIVIDE exp'
    p[0] = (p[1][0], 'divide', p[1], p[3])

def p_exp_lt(p):
    'exp : exp LT exp'
    p[0] = (p[1][0], 'lt', p[1], p[3])

def p_exp_le(p):
    'exp : exp LE exp'
    p[0] = (p[1][0], 'le', p[1], p[3])

def p_exp_eq(p):
    'exp : exp EQUAL exp'
    p[0] = (p[1][0], 'eq', p[1], p[3])

def p_exp_not(p):
    'exp : NOT exp'
    p[0] = (p.lineno(1), 'not', p[2])

def p_exp_negate(p):
    'exp : TILDE exp'
    p[0] = (p.lineno(1), 'negate', p[2])
'''
def p_exp_parenexp(p): #NOT REQUIRED BY ASSIGNMENT, BUT MENTIONED IN GRAMMAR
    'exp : LPAREN exp RPAREN'
    p[0] = (p.lineno(1), 'paren_exp', p[2])
'''
def p_exp_identifier(p):
    'exp : identifier'
    p[0] = (p[1][0], 'identifier', p[1])

def p_exp_integer(p):
    'exp : INTEGER'
    p[0] = (p.lineno(1), 'integer', p[1])

def p_exp_string(p):
    'exp : STRING'
    p[0] = (p.lineno(1), 'string', p[1])

def p_exp_true(p):
    'exp : TRUE'
    p[0] = (p.lineno(1), 'true')

def p_exp_false(p):
    'exp : FALSE'
    p[0] = (p.lineno(1), 'false')

#LET EXPRESSION -- done

def p_exp_let(p):
    'exp : LET attribute attributelist IN exp'
    p[0]= (p.lineno(1), 'let', [p[2]]+p[3], p[5])

def p_let_attributelist_none(p):
    'attributelist : '
    p[0] = []

def p_let_attrubutelist_some(p):
    'attributelist : COMMA attribute attributelist'
    p[0] = [p[2]] + p[3]

#CASE EXPRESSIONS -- done

def p_exp_case(p):
    'exp : CASE exp OF elementlist ESAC'
    p[0] = (p.lineno(1), 'case', p[2], p[4])

def p_case_element(p):
    'element : identifier COLON type RARROW exp'
    p[0] = (p[1][0], p[1], p[3], p[5])

def p_case_elementlist_one(p):
    'elementlist : element SEMI'
    p[0] = [p[1]]

def p_case_elementlist_some(p):
    'elementlist : element SEMI elementlist'
    p[0] = [p[1]] + p[3]

#ERROR -- done

def p_error(p):
    if p:
        print("ERROR:", p.lineno, ": Parser: parse error near", p.value)
        exit(1)
    else:
        print("ERROR: Syntax error at EOF") 
        exit(1)

#Build PA3 Parser from above rules

parser = yacc.yacc()
ast = yacc.parse(lexer=pa2lexer)

#print(ast) #For testing

#Want to output cl-ast file

ast_filename = (sys.argv[1])[:-3] + "ast" #FOR FINISHED PRODUCT
#ast_filename = tokens_filename[:-3] + "ast" #FOR TESTING
fout = open(ast_filename, 'w')

#Define a number of print_foo() methods
#that call each other to serialzie the AST.

def print_list(ast, print_element_function): #Higher-order function
    fout.write(str(len(ast)) + "\n")
    for elem in ast:
        print_element_function(elem)

def print_identifier(ast):
    #ast = (p.lineno(1), p[1])
    fout.write(str(ast[0]) + "\n")
    fout.write(ast[1] + "\n")

def print_exp(ast):
    fout.write(str(ast[0]) + "\n")
    fout.write(ast[1] + "\n")
    if ast[1] in ['plus', 'minus', 'times', 'divide', 'lt', 'le', 'eq', 'while']:
        #ast = (p.lineno(1), 'plus', p[1], p[3])
        print_exp(ast[2])
        print_exp(ast[3])

    elif ast[1] == 'if':
        #ast = (p.lineno(1), 'if', p[2], p[4], p[6])
        print_exp(ast[2])
        print_exp(ast[3])
        print_exp(ast[4])
    elif ast[1] == 'assign':
        #ast = (p[1][0], 'assign', p[1], p[3])
        print_identifier(ast[2])
        print_exp(ast[3])
    elif ast[1] == 'block':
        #ast = (p.lineno(1), 'block', p[2])
        print_list(ast[2], print_exp)
    elif ast[1] == 'dynamic_dispatch':
        #ast = (p[1][0], 'dynamic_dispatch', p[1], p[3], p[5])
        print_exp(ast[2])
        print_identifier(ast[3])
        print_list(ast[4], print_exp)
    elif ast[1] == 'static_dispatch':
        #ast = (p[1][0], 'static_dispatch', p[1], p[3], p[5], p[7])
        print_exp(ast[2])
        print_identifier(ast[3])
        print_identifier(ast[4])
        print_list(ast[5], print_exp)
    elif ast[1] == 'self_dispatch':
        #ast = (p[1][0], 'self_dispatch', p[1], p[3])
        print_identifier(ast[2])
        print_list(ast[3], print_exp)
    elif ast[1] in ['integer', 'string']:
        #ast = (p.lineno(1), 'integer', p[1])
        fout.write(str(ast[2]) + "\n")
    elif ast[1] in ['isvoid', 'not', 'negate', 'paren_exp']:
        #ast = (p.lineno(1), 'isvoid', p[2])
        print_exp(ast[2])
    elif ast[1] in ['new', 'identifier']:
        #ast = (p.lineno(1), 'new', p[2])
        print_identifier(ast[2])
    elif ast[1] == 'let':
        #ast = (p.lineno(1), 'let', [p[2]]+p[3], p[5])
        print_list(ast[2], print_binding)
        print_exp(ast[3])
    elif ast[1] == 'case':
        #ast = (p.lineno(1), 'case', p[2], p[4])
        print_exp(ast[2])
        print_list(ast[3], print_element)
    else:
        print("unhandled expression")
        exit(1)

def print_element(ast):
    #ast = (p[1][0], p[1], p[3], p[5])
    print_identifier(ast[1])
    print_identifier(ast[2])
    print_exp(ast[3])

def print_binding(ast):
    #Similar to print_feature below
    if ast[1] == 'attribute_no_init':
        fout.write("let_binding_no_init\n")
        print_identifier(ast[2])
        print_identifier(ast[3])
    elif ast[1] == 'attribute_init':
        fout.write("let_binding_init\n")
        print_identifire(ast[2])
        print_identifier(ast[3])
        print_exp(ast[4])

def print_feature(ast):
    if ast[1] == 'attribute_no_init':
        #ast = (p.lineno(1), 'attribute_no_init', p[1], p[3])
        fout.write("attribute_no_init\n")
        print_identifire(ast[2])
        print_identifier(ast[3])
    elif ast[1] == 'attribute_init':
        #ast = (p.lineno(1), 'attribute_init', p[1], p[3], p[5])
        fout.write("attribute_init\n")
        print_identifire(ast[2])
        print_identifier(ast[3])
        print_exp(ast[4])
    elif ast[1] == 'method':
        #ast = (p[1][0], 'method_withformals', p[1], p[3]/[], p[6], p[8])
        fout.write("method\n")
        print_identifier(ast[2])
        print_list(ast[3], print_formal)
        fout.write("\n")
        print_identifier(ast[4])
        print_exp(ast[5])
    else:
        print("unhandled feature")
        exit(1)

def print_class(ast):
    if ast[1] == 'class_noinherit':
        #ast = (p.lineno(1) , 'class_noinherit' , p[2] name, p[4] feature list)
        print_identifier(ast[2])
        fout.write("class_noinherit\n")
        print_list(ast[3], print_feature)
    elif ast[1] == 'class_inherit':
        #ast = (p.lineno(1), 'class_inherit', p[2], p[4], p[6])
        print_identifier(ast[2])
        fout.write("class_inherit\n")
        print_identifier(ast[3])
        print_list(ast[4], print_feature)
    else:
        print("unhandled class")
        exit(1)

def print_formal(ast):
    #ast = (p[1][0], p[1], p[3])
    print_identifier(ast[1])
    print_identifier(ast[2])

def print_program(ast):
    print_list(ast, print_class)

print_program(ast)

fout.close()
    
