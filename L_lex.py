#! /usr/bin/env python
# coding=utf8


import lex
import re


tokens = (
    'IF', 'THEN', 'ELSE', 
    'WHILE', 'DO', 
    'READ', 'WRITE',
    'BEGIN', 'END',
    'PLUS', 'MINUS', 'MULT', 'DIV', 'MOD', 'POW',
    'EQ', 'NEQ',
    'GT', 'GE', 'LT', 'LE', 
    'AND', 'OR',
    'TRUE', 'FALSE',
    'SEMICOLON',
    'LBRACKET', 'RBRACKET',
    'VAR',
    'NUM',
    'COMMENT',
    'MLBODY',
    'ASSIGN',
    'SKIP'
)

def build_lexer():

    states = (
       ('mlcomment','exclusive'),
              
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
        r'skip' : 'SKIP'
    }


    t_PLUS  = r'\+';
    t_MINUS = r'-';
    t_MULT  = r'\*';
    t_DIV   = r'/';
    t_MOD   = r'%';
    t_POW   = r'\*\*';
    t_EQ  = r'==';
    t_NEQ = r'!=';
    t_GT  = r'>';
    t_GE  = r'>=';
    t_LT  = r'<';
    t_LE  = r'<=';
    t_AND = r'&&';
    t_OR  = r'\|\|';
    t_ASSIGN  = r':=';


    t_SEMICOLON = r';';
    t_LBRACKET = r'\(';
    t_RBRACKET = r'\)';

    t_NUM = r'-?[1-9][0-9]*(\.([0-9]*[1-9]|0))?(e(\+|-)[0-9]*[1-9])?|-?0?\.[0-9]*[1-9](e(\+|-)[0-9]*[1-9])?|0'

    t_COMMENT = r'[ \t]*\/\/[^\r\n\f]*'

    def t_VAR(t):
        r'[a-zA-Z_][a-zA-Z_0-9]*'
        t.type = reserved.get(t.value, 'VAR')    # Check for reserved words
        return t

    t_ignore = ' \r\t\f'

    def t_newline(t):
        r'\n+'
        t.lexer.lineno += len(t.value)
        t.lexer.last_line_start_position = t.lexpos


    def t_ANY_error(t):
        try:
            line_start_pos = t.lexer.last_line_start_position
        except AttributeError:
            line_start_pos = -1

        print("Illegal character {} at {} {}".format(t.value[0], t.lineno - 1, t.lexpos - line_start_pos - 1))
        t.lexer.skip(1)


    # for state MLCOMMENT
    def t_mlcomment_MLBODY(t): 
        r'(\**[^\*\)]+\/*)+'
        num_newlines = t.value.count('\n')
        t.lexer.lineno += num_newlines
        t.lexer.last_line_start_position = t.value.rfind('\n')
        return t
        

    t_mlcomment_ignore = '\r\f'

    def t_begin_mlcomment(t): 
        r'\(\*'
        t.lexer.begin('mlcomment')

    def t_mlcomment_end(t):
        r'\*\)'
        t.lexer.begin('INITIAL')  




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

def print_tokens(tokens_it, data, should_filter=False):
    lines = []
    for t in tokens_it:
        if should_filter and t.type in ('COMMENT', 'MLBODY'):
            continue
        col = find_column(data, t)
        if t.type != 'MLBODY': 
            lines.append(''.join([(t.type + ':').ljust(12),  
                         str(t.lineno - 1), ' ', 
                         str(col) + '-' + str(col + len(t.value) - 1),
                         ',{}\"'.format(' ') + t.value +\
                         '\"' if t.type in ('VAR', 'NUM', 'COMMENT') else '']))
        else:
            num_newlines = t.value.count('\n')
            if num_newlines != 0:
                lastlinepos = len(t.value) - 1 - t.value.rfind('\n')
            else:
                lastlinepos = col + len(t.value) - 1
            lines.append(''.join([(t.type + ':').ljust(12),  
                     str(t.lineno - 1) + ':' + str(col), ' - ',
                     str(t.lineno - 1 + num_newlines) + ':' +\
                        str(lastlinepos),
                     ',{}\"'.format('\n') + t.value + '\"']))
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


def test4():
    lexer = build_lexer()
    data = '''
false
    i == 0 write;
    do
        i == i + 159000;
    begin (_i_FGH != 10);
end
'''
    expected = ["FALSE:".ljust(12) + "1 0-4",
                "VAR:".ljust(12) + "2 4-4, \"i\"",
                "EQ:".ljust(12) + "2 6-7",
                "NUM:".ljust(12) + "2 9-9, \"0\"",
                "WRITE:".ljust(12) + "2 11-15",
                "SEMICOLON:".ljust(12) + "2 16-16",
                "DO:".ljust(12) + "3 4-5",
                "VAR:".ljust(12) + "4 8-8, \"i\"",
                "EQ:".ljust(12) + "4 10-11",
                "VAR:".ljust(12) + "4 13-13, \"i\"",
                "PLUS:".ljust(12) + "4 15-15",
                "NUM:".ljust(12) + "4 17-22, \"159000\"",
                "SEMICOLON:".ljust(12) + "4 23-23",
                "BEGIN:".ljust(12) + "5 4-8",
                "LBRACKET:".ljust(12) + "5 10-10",
                "VAR:".ljust(12) + "5 11-16, \"_i_FGH\"",
                "NEQ:".ljust(12) + "5 18-19",
                "NUM:".ljust(12) + "5 21-22, \"10\"",
                "RBRACKET:".ljust(12) + "5 23-23",
                "SEMICOLON:".ljust(12) + "5 24-24",
                "END:".ljust(12) + "6 0-2"] 
    lexer.input(data)
    actual = print_tokens(gen_tokens(lexer), data)
    if expected != actual:
        fail("test 4 failed")


def test5():
    lexer = build_lexer()
    data = '''read x; 
(*if y + 1.24e+5 == x 
this is
a multiline
comment with stars * ,  
double stars ** , slashes // and
even mlstart (* in it *)
then 
x := 2 ** 0.5 * 4 (* the end *)
'''
    expected = ["READ:".ljust(12) + "0 0-3",
                "VAR:".ljust(12) + "0 5-5, \"x\"",
                "SEMICOLON:".ljust(12) + "0 6-6",
                "MLBODY:".ljust(12) + "1:2 - 6:22," + '''
\"if y + 1.24e+5 == x 
this is
a multiline
comment with stars * ,  
double stars ** , slashes // and
even mlstart (* in it \"''',
                "THEN:".ljust(12) + "7 0-3",
                "VAR:".ljust(12) + "8 0-0, \"x\"",
                "ASSIGN:".ljust(12) + "8 2-3",
                "NUM:".ljust(12) + "8 5-5, \"2\"",
                "POW:".ljust(12) + "8 7-8",
                "NUM:".ljust(12) + "8 10-12, \"0.5\"",
                "MULT:".ljust(12) + "8 14-14",
                "NUM:".ljust(12) + "8 16-16, \"4\"",
                "MLBODY:".ljust(12) + "8:20 - 8:28," + '''
\" the end \"''',] 
    lexer.input(data)
    actual = print_tokens(gen_tokens(lexer), data)
    if expected != actual:
        for i in range(len(actual)):
            if actual[i] != expected[i]:
                print actual[i]
                print expected[i]
        fail("test 5 failed")


from argparse import ArgumentParser

def main():
    parser = ArgumentParser()
    parser.add_argument('-i', '--input', help='path to the input file')
    parser.add_argument('-f', '--filter', action='store_true', help='filter the commentaries')
    args = parser.parse_args()

    # with open(args.input) as inp:
    #     data = [st.strip().split('//')[0] for st in inp]
    # data = '\n'.join(data)
    with open(args.input) as inp:
        data = ''.join([st for st in inp])
    lexer = build_lexer()
    lexer.input(data)
    print('\n'.join(print_tokens(gen_tokens(lexer), data, args.filter)))


if __name__ == '__main__':
    test1()
    test2()
    test3()
    test4()
    test5()
    main()

