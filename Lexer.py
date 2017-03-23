#! /usr/bin/env python
# coding=utf8


import lex
import re


def build_lexer():
    tokens = (
        'IF', 'THEN', 'ELSE', 
        'WHILE', 'DO', 
        'READ', 'WRITE',
        'BEGIN', 'END',
        'PLUS', 'MINUS', 'MULT', 'DIV', 'MOD',
        'EQ', 'NEQ',
        'GT', 'GE', 'LT', 'LE', 
        'AND', 'OR',
        'TRUE', 'FALSE',
        'SEMICOLON',
        'LBRACKET', 'RBRACKET',
        'VAR',
        'NUM'
    )

    reserved = {
        r'if' : 'IF',
        r'then' : 'THEN',
        r'else' : 'ELSE',
        r'true' : 'TRUE',
        r'false' : 'FALSE',
        r'while' : 'WHILE',
        r'do' : 'DO',
        r'read' : 'READ',
        r'write' : 'WRITE',
        r'begin' : 'BEGIN',
        r'end' : 'END',
    }


    t_PLUS  = r'\+';
    t_MINUS = r'-';
    t_MULT  = r'\*';
    t_DIV   = r'/';
    t_MOD   = r'%';
    t_EQ  = r'==';
    t_NEQ = r'!=';
    t_GT  = r'>';
    t_GE  = r'>=';
    t_LT  = r'<';
    t_LE  = r'<=';
    t_AND = r'&&';
    t_OR  = r'\|\|';


    t_SEMICOLON = r';';
    t_LBRACKET = r'\(';
    t_RBRACKET = r'\)';


    t_NUM = r'-?[1-9][0-9]*(\.[0-9]*[1-9])?(e(\+|-)[0-9]*[1-9])?|-?0?\.[0-9]*[1-9](e(\+|-)[0-9]*[1-9])?|0'



    def t_VAR(t):
        r'[a-zA-Z_][a-zA-Z_0-9]*'
        t.type = reserved.get(t.value, 'VAR')    # Check for reserved words
        return t

    t_ignore = ' \r\t\f'

    def t_newline(t):
        r'\n+'
        t.lexer.lineno += len(t.value)


    def t_error(t):
        print("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)

    lexer = lex.lex(reflags=re.UNICODE | re.DOTALL)

    return lexer



def find_column(input, token):
    last_cr = input.rfind('\n', 0, token.lexpos)
    if last_cr < 0:
        return token.lexpos 
    return (token.lexpos - last_cr) - 1



def gen_tokens(lexer):
    tok = lexer.token()
    while tok:
        yield tok
        tok = lexer.token()     

def print_tokens(tokens_it, data):
    lines = []
    for t in tokens_it:
        col = find_column(data, t)
        lines.append(''.join([(t.type + ':').ljust(12),  
                     str(t.lineno - 1), ' ', 
                     str(col) + '-' + str(col + len(t.value) - 1),
                     ', \"' + t.value + '\"' if t.type in ('VAR', 'NUM') else '']))
    return lines


def fail(msg):
    raise Exception(msg)



def test1():
    lexer = build_lexer()
    data = '''read x;'''
    expected = ["READ:".ljust(12) + "0 0-3", 
                "VAR:".ljust(12) + "0 5-5, \"x\"",
                "SEMICOLON:".ljust(12) + "0 6-6"]
    
    lexer.input(data)
    actual = print_tokens(gen_tokens(lexer), data)

    if expected != actual:
        fail("test 1 failed")

def test2():
    lexer = build_lexer()
    data = '''
if true
then
write 1.2e+4
'''
    expected = ["IF:".ljust(12) + "1 0-1",
                "TRUE:".ljust(12) + "1 3-6",
                "THEN:".ljust(12) + "2 0-3", 
                "WRITE:".ljust(12) + "3 0-4",
                "NUM:".ljust(12) + "3 6-11, \"1.2e+4\""] 
    lexer.input(data)
    actual = print_tokens(gen_tokens(lexer), data)
    if expected != actual:
        fail("test 2 failed")

def test3():
    lexer = build_lexer()
    data = '''
begin
    i == 0;
    do
        i == i + 1;
    while (i < 10);
end
'''
    expected = ["BEGIN:".ljust(12) + "1 0-4",
                "VAR:".ljust(12) + "2 4-4, \"i\"",
                "EQ:".ljust(12) + "2 6-7",
                "NUM:".ljust(12) + "2 9-9, \"0\"",
                "SEMICOLON:".ljust(12) + "2 10-10",
                "DO:".ljust(12) + "3 4-5",
                "VAR:".ljust(12) + "4 8-8, \"i\"",
                "EQ:".ljust(12) + "4 10-11",
                "VAR:".ljust(12) + "4 13-13, \"i\"",
                "PLUS:".ljust(12) + "4 15-15",
                "NUM:".ljust(12) + "4 17-17, \"1\"",
                "SEMICOLON:".ljust(12) + "4 18-18",
                "WHILE:".ljust(12) + "5 4-8",
                "LBRACKET:".ljust(12) + "5 10-10",
                "VAR:".ljust(12) + "5 11-11, \"i\"",
                "LT:".ljust(12) + "5 13-13",
                "NUM:".ljust(12) + "5 15-16, \"10\"",
                "RBRACKET:".ljust(12) + "5 17-17",
                "SEMICOLON:".ljust(12) + "5 18-18",
                "END:".ljust(12) + "6 0-2"] 
    lexer.input(data)
    actual = print_tokens(gen_tokens(lexer), data)
    if expected != actual:
        fail("test 3 failed")

from argparse import ArgumentParser

def main():
    parser = ArgumentParser()
    parser.add_argument('-i', '--input', help='path to the input file')
    args = parser.parse_args()

    with open(args.input) as inp:
        data = [st.strip().split('//')[0] for st in inp]
    data = '\n'.join(data)
    lexer = build_lexer()
    lexer.input(data)
    print('\n'.join(print_tokens(gen_tokens(lexer), data)))


if __name__ == '__main__':
    test1()
    test2()
    test3()
    main()

