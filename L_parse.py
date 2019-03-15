#! /usr/bin/env python2

from argparse import ArgumentParser
from L_lex import *
import yacc



precedence = (
    ('left', 'OR'), 
    ('left', 'AND'), 
    # ('nonassoc', 'NOT'), 
    ('nonassoc', 'EQ', 'NEQ'),  # Nonassociative operators
    ('nonassoc', 'LE', 'GE', 'GT'),  # Nonassociative operators
    ('left', 'PLUS', 'MINUS'),
    ('left', 'MULT', 'DIV', 'MOD'), 
    ('left', 'POW') 
)
parser = ''
top_statement = ['']
top_program = ['']

def p_program(p):
    '''program : definition SEMICOLON program
               | programbody 
               |'''
    p[0] = {'program' : (p[1], p[3]) if len(p) > 2 else (p[1] if len(p) == 2 else '')}
    top_program[0] = p[0] 
def p_programbody(p):
    '''programbody : statement SEMICOLON programbody
                   | statement'''
    p[0] = {'program body' : (p[1], p[3]) if len(p) > 2 else p[1]}
 

def p_definition(p):
    '''definition : functioncall FUNASSIGN BEGIN programbody END
                  | functioncall FUNASSIGN BEGIN programbody RETURN expression END
                  | functioncall FUNASSIGN BEGIN expression END
                  | functioncall FUNASSIGN BEGIN RETURN expression END'''
    if len(p) == 6:
        p[0] = {'function definition' : (p[1], p[4])}
    elif len(p) == 7:
        p[0] = {'function definition' : (p[1], p[5])}
    elif len(p) == 8:
        p[0] = {'function definition' : (p[1], p[4], p[5], p[6])}

    top_statement[0] = p[0]
def p_functioncall(p):
    '''functioncall : FUN functionargs RBRACKET
                    | VAR LBRACKET functionargs RBRACKET'''
    if len(p) == 4:
        p[0] = {'function call' : (p[1][:-1], p[2])}
    elif len(p) == 5:
        p[0] = {'function call' : (p[1], p[3])}
def p_functionargs(p):
    '''functionargs : VAR
                    | VAR COMMA functionargs
                    |'''
    p[0] = {'function arguments' : '' if len(p) < 2 else (p[1] if len(p) < 3 else (p[1], p[3]))}

def p_statement_skip(p):
    '''statement : SKIP'''
    p[0] = {'skip statement': 'skip'}
    top_statement[0] = p[0]
def p_statement_assign(p):
    '''statement : VAR ASSIGN expression'''
    p[0] = {'assignment' : (p[1], p[3])}
    top_statement[0] = p[0]
def p_statement_functioncall(p):
    '''statement : functioncall'''
    p[0] = {'function call (as statement)' : p[1]}
    top_statement[0] = p[0]
# def p_statement_semicolon(p):
#     '''statement : statement SEMICOLON statement'''
#     p[0] = (p[1], p[3])
#     top_statement[0] = p[0]
def p_statement_write(p):
    '''statement : WRITEBR expression RBRACKET
                 | WRITE LBRACKET expression RBRACKET'''
    if len(p) == 4:
        p[0] = {'write statement' : p[2]}
    elif len(p) == 5:
        p[0] = {'write statement' : p[3]}
    top_statement[0] = p[0]
def p_statement_writeassign(p):
    '''statement : VAR WRITEASSIGN expression'''
    p[0] = ({'assignment' : (p[1], p[3])}, {'program body': {'write statement' : p[1]}})
def p_statement_read(p):
    '''statement : READBR VAR RBRACKET 
                 | READ LBRACKET VAR RBRACKET'''
    if len(p) == 4:
        p[0] = {'read statement' : p[2]}
    elif len(p) == 5:
        p[0] = {'read statement' : p[3]}
    top_statement[0] = p[0]
def p_statement_while(p):
    '''statement : WHILE LBRACKET expression RBRACKET DO BEGIN programbody END'''
    p[0] = {'while statement' : ({'while condition' : p[3]}, {'while body' :  p[7]})}
    top_statement[0] = p[0]
def p_statement_if(p):
    '''statement : IF LBRACKET expression RBRACKET THEN BEGIN programbody END ELSE BEGIN programbody END'''
                 # | UNLESS LBRACKET expression RBRACKET THEN BEGIN programbody END ELSE BEGIN programbody END'''
    if p[1] == 'if':
        p[0] = {'if statement' : ({'if condition' : p[3]},  {'then body' : p[7]}, {'else body' : p[11]})}
    # else:
    #     p[0] = {'if statement' : ({'if condition' : {'NOT expression' : p[3]}},  {'then body' : p[7]}, {'else body' : p[11]})}
    top_statement[0] = p[0]

def p_expression(p):
    '''expression : VAR
                  | NUM
                  | TRUE
                  | FALSE
                  | functioncall'''
    p[0] = p[1]
def p_expression_binary_op(p):
    '''expression : expression MULT expression'''
    p[0] = {'* expression' : (p[1] , p[3])}
def p_expression_pow(p):
    '''expression : expression POW expression'''
    p[0] = {'** expression' : (p[1] , p[3])}
def p_expression_div(p):
    '''expression : expression DIV expression'''
    p[0] = {'/ expression' : (p[1] , p[3])}
    
def p_expression_mod(p):
    '''expression : expression MOD expression'''
    p[0] = {'\% \expression' : (p[1] , p[3])}
    
def p_expression_plus(p):
    '''expression : expression PLUS expression'''
    p[0] = {'+ expression' : (p[1] , p[3])}
    
def p_expression_minus(p):
    '''expression : expression MINUS expression'''
    p[0] = {'- expression' : (p[1] , p[3])}
    
def p_expression_gt(p):
    '''expression : expression GT expression'''
    p[0] = {'> expression' : (p[1] , p[3])}
    
def p_expression_ge(p):
    '''expression : expression GE expression'''
    p[0] = {'>= expression' : (p[1] , p[3])}
    
def p_expression_lt(p):
    '''expression : expression LT expression'''
    p[0] = {'< expression' : (p[1] , p[3])}
    
def p_expression_le(p):
    '''expression : expression LE expression'''
    p[0] = {'<= expression' : (p[1] , p[3])}
    
def p_expression_eq(p):
    '''expression : expression EQ expression'''
    p[0] = {'== expression' : (p[1] , p[3])}
    
def p_expression_neq(p):
    '''expression : expression NEQ expression'''
    p[0] = {'!= expression' : (p[1] , p[3])}
    
def p_expression_and(p):
    '''expression : expression AND expression'''
    p[0] = {'&& expression' : (p[1] , p[3])}
    
def p_expression_or(p):
    '''expression : expression OR expression'''
    p[0] = {'|| expression' : (p[1] , p[3])}
    
# def p_expression_not(p):
#     '''expression : NOT expression'''
#     p[0] = {'NOT expression' : (p[2])}
    

def p_expression_brackets(p):
    '''expression : LBRACKET expression RBRACKET'''
    p[0] = {'brackets expression' : p[2]}
    


def p_statement_multassign(p):
    '''statement : VAR MULTASSIGN expression'''
    p[0] = {'assignment' : (p[1], {'* expression' : (p[1] , p[3])})}
    top_statement[0] = p[0]
def p_statement_powassign(p):
    '''statement : VAR POWASSIGN expression'''
    p[0] = {'assignment' : (p[1], {'** expression' : (p[1] , p[3])})}
    top_statement[0] = p[0]
def p_statement_divassign(p):
    '''statement : VAR DIVASSIGN expression'''
    p[0] = {'assignment' : (p[1], {'/ expression' : (p[1] , p[3])})}
    top_statement[0] = p[0]
def p_statement_modassign(p):
    '''statement : VAR MODASSIGN expression'''
    p[0] = {'assignment' : (p[1], {'\% \expression' : (p[1] , p[3])})}
    top_statement[0] = p[0]
def p_statement_plusassign(p):
    '''statement : VAR PLUSASSIGN expression'''
    p[0] = {'assignment' : (p[1], {'+ expression' : (p[1] , p[3])})}
    top_statement[0] = p[0]
def p_statement_minusassign(p):
    '''statement : VAR MINUSASSIGN expression'''
    p[0] = {'assignment' : (p[1], {'- expression' : (p[1] , p[3])})}
    top_statement[0] = p[0]

def p_statement_andassign(p):
    '''statement : VAR ANDASSIGN expression'''
    p[0] = {'assignment' : (p[1], {'AND expression' : (p[1] , p[3])})}
    top_statement[0] = p[0]
def p_statement_orassign(p):
    '''statement : VAR ORASSIGN expression'''
    p[0] = {'assignment' : (p[1], {'OR expression' : (p[1] , p[3])})}
    top_statement[0] = p[0]



def p_error(p):
    print("Syntax error in input!", p)
    raise Exception


def get_string_program(lines,program, prefix=''):
    if type(program) == tuple:
        for subprogram in program:
            get_string_program(lines, subprogram, prefix)
    elif type(program) == dict:
        for p in program:
            lines.append(prefix + p + ':')
            get_string_program(lines, program[p], prefix + '\t')
    else:
        lines.append(prefix + program)

def print_program(program):
    lines = []
    get_string_program(lines, program, '')
    print '\n'.join(lines)

    # if type(program) == tuple:
    #     # print 'tpl'
    #     for subprogram in program:
    #         print_program(subprogram, prefix)
    # elif type(program) == dict:
    #     # print 'dct'
    #     # print program
    #     for p in program:
    #         print(prefix + p + ':')
    #         print_program(program[p], prefix + '\t')
    # else:
    #     print prefix + program




def parser_test1(parser):
    # parser = yacc.yacc()
    data = '''read(x)'''

    expected = \
'''program:
\tprogram body:
\t\tread statement:
\t\t\tx'''
    lexer = build_lexer()
    parser.parse(input=data, lexer=lexer)
    actual_lines = []
    get_string_program(actual_lines, top_program[0])
    actual = '\n'.join(actual_lines)
    if expected != actual:
        fail("test 1 failed") 
    top_program[0] = ''

def parser_test2(parser):
    # parser = yacc.yacc()
    data = '''
if (true)
then begin
write(1.2e+4)
end
else begin
fun(x)
end
'''
    expected = \
'''program:
\tprogram body:
\t\tif statement:
\t\t\tif condition:
\t\t\t\ttrue
\t\t\tthen body:
\t\t\t\tprogram body:
\t\t\t\t\twrite statement:
\t\t\t\t\t\t1.2e+4
\t\t\telse body:
\t\t\t\tprogram body:
\t\t\t\t\tfunction call (as statement):
\t\t\t\t\t\tfunction call:
\t\t\t\t\t\t\tfun
\t\t\t\t\t\t\tfunction arguments:
\t\t\t\t\t\t\t\tx''' 
    lexer = build_lexer()
    parser.parse(input=data, lexer=lexer)
    actual_lines = []
    get_string_program(actual_lines, top_program[0])
    actual = '\n'.join(actual_lines)
    if expected != actual:
        fail("test 2 failed")
    top_program[0] = ''

def parser_test3(parser):
    # parser = yacc.yacc()
    data = '''
f(x) <- begin
read(x);
x := x + 1
return x * x
end;
if (true)
then begin
y := 2;
x := fun(y);
write(y)
end
else begin
fun(z)
end
'''
    expected = \
'''program:
\tfunction definition:
\t\tfunction call:
\t\t\tf
\t\t\tfunction arguments:
\t\t\t\tx
\t\tprogram body:
\t\t\tread statement:
\t\t\t\tx
\t\t\tprogram body:
\t\t\t\tassignment:
\t\t\t\t\tx
\t\t\t\t\t+ expression:
\t\t\t\t\t\tx
\t\t\t\t\t\t1
\t\treturn
\t\t* expression:
\t\t\tx
\t\t\tx
\tprogram:
\t\tprogram body:
\t\t\tif statement:
\t\t\t\tif condition:
\t\t\t\t\ttrue
\t\t\t\tthen body:
\t\t\t\t\tprogram body:
\t\t\t\t\t\tassignment:
\t\t\t\t\t\t\ty
\t\t\t\t\t\t\t2
\t\t\t\t\t\tprogram body:
\t\t\t\t\t\t\tassignment:
\t\t\t\t\t\t\t\tx
\t\t\t\t\t\t\t\tfunction call:
\t\t\t\t\t\t\t\t\tfun
\t\t\t\t\t\t\t\t\tfunction arguments:
\t\t\t\t\t\t\t\t\t\ty
\t\t\t\t\t\t\tprogram body:
\t\t\t\t\t\t\t\twrite statement:
\t\t\t\t\t\t\t\t\ty
\t\t\t\telse body:
\t\t\t\t\tprogram body:
\t\t\t\t\t\tfunction call (as statement):
\t\t\t\t\t\t\tfunction call:
\t\t\t\t\t\t\t\tfun
\t\t\t\t\t\t\t\tfunction arguments:
\t\t\t\t\t\t\t\t\tz''' 
    lexer = build_lexer()
    parser.parse(input=data, lexer=lexer)
    actual_lines = []
    get_string_program(actual_lines, top_program[0])
    actual = '\n'.join(actual_lines)
    if expected != actual:
        fail("test 3 failed")
    top_program[0] = ''




def main():
    parser = yacc.yacc()
    parser_test1(parser)
    parser_test2(parser)
    parser_test3(parser)
    top_program[0] = ''
    argparser = ArgumentParser()
    argparser.add_argument("-i", "--input", help="input file with L program to parse", required=True)
    args = argparser.parse_args()

    with open(args.input) as inp:
        data = ''.join(inp)
    lexer = build_lexer()
    # try:
    parser.parse(input=data, lexer=lexer)
    # except Exception:
    #   print "parsing terminated"
    #   return
    print_program(top_program[0])


if __name__ == '__main__':
    main()


