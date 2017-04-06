from L_lex import *
import yacc

# def p_expression(p):
#     '''expression : expression PLUS expression
#                 | expression PLUS expression'''
#     print (p[1] + '+' + p[2])




precedence = (
    ('left', 'OR'), 
    ('left', 'AND'), 
    ('nonassoc', 'EQ', 'NEQ'),  # Nonassociative operators
    ('nonassoc', 'LE', 'GE', 'GT', 'GE'),  # Nonassociative operators
    ('left', 'PLUS', 'MINUS'),
    ('left', 'MULT', 'DIV', 'MOD') 
)

top_statement = ['']



def p_statement_skip(p):
    '''statement : SKIP'''
    p[0] = {'skip statement': 'skip'}
    top_statement[0] = p[0]
def p_statement_assign(p):
    '''statement : VAR ASSIGN expression'''
    p[0] = {'assignment' : (p[1], p[3])}
    top_statement[0] = p[0]
def p_statement_semicolon(p):
    '''statement : statement SEMICOLON statement'''
    p[0] = (p[1], p[3])
    top_statement[0] = p[0]
def p_statement_write(p):
    '''statement : WRITE LBRACKET expression RBRACKET'''
    p[0] = {'write statement' : p[3]}
    top_statement[0] = p[0]
def p_statement_read(p):
    '''statement : READ LBRACKET VAR RBRACKET'''
    p[0] = {'read statement' : p[3]}
    top_statement[0] = p[0]
def p_statement_while(p):
    '''statement : WHILE LBRACKET expression RBRACKET DO BEGIN statement END'''
    p[0] = {'while statement' : ({'while condition' : p[3]}, {'while body' :  p[7]})}
    top_statement[0] = p[0]
def p_statement_if(p):
    '''statement : IF LBRACKET expression RBRACKET THEN BEGIN statement END ELSE BEGIN statement END'''
    p[0] = {'if statement' : ({'if condition' : p[3]},  {'then body' : p[7]}, {'else body' : p[11]})}
    top_statement[0] = p[0]

def p_expression(p):
    '''expression : VAR
                  | NUM
                  | TRUE
                  | FALSE'''
    p[0] = p[1]
def p_expression_binary_op(p):
    '''expression : expression MULT expression'''
    p[0] = {'* expression' : (p[1] , p[3])}
def p_expression_div(p):
    '''expression : expression DIV expression'''
    p[0] = {'/ expression' : (p[1] , p[3])}
    
def p_expression_mod(p):
    '''expression : expression MOD expression'''
    p[0] = {'% expression' : (p[1] , p[3])}
    
def p_expression_plus(p):
    '''expression : expression PLUS expression'''
    p[0] = {'+ expression' : (p[1] , p[3])}
    
def p_expression_minus(p):
    '''expression : expression MINUS expression'''
    p[0] = {'/ expression' : (p[1] , p[3])}
    
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
    


def p_expression_brackets(p):
    '''expression : LBRACKET expression RBRACKET'''
    p[0] = {'brackets expression' : p[2]}
    




def p_error(p):
    print("Syntax error in input!")


def print_program(program, prefix=''):
    if type(program) == tuple:
        # print 'tpl'
        for subprogram in program:
            print_program(subprogram, prefix)
    elif type(program) == dict:
        # print 'dct'
        # print program
        for p in program:
            print(prefix + p + ':')
            print_program(program[p], prefix + '\t')
    else:
        print prefix + program


parser = yacc.yacc()

data = '''if (false) 
            then begin 
                while (1) do begin 
                    read(y); x := (2 + (1 + x) * y); skip; write(x + y) 
                end 
            end 
            else begin 
                write (2)
            end;
            end_program := true'''
# data = "if (1) then begin a := 1 end else begin write(1) end"
# data = "skip"
lexer = build_lexer()
# lexer.input(data)
# print('\n'.join(print_tokens(gen_tokens(lexer), data, False)))
parser.parse(input=data, lexer=lexer)
print_program(top_statement[0])
# print(type(top_statement[0][0]['if statement']))