# JetBrains Academy - Core Python course
# Smart Calculator project - Stage 7/7
# https://hyperskill.org/projects/74
# submitted by Chris Freeman - 04-Jan-2023

# GLOBAL DATA
variables = {}      # Global dictionary of (name, value) variables
operators = ["+", "-", "*", "/"]    # global list of operator tokens
p_table = {'+': 0, '-': 0, '*': 1, '/': 1}  # Operator Precedence lookup table
brackets = ['(', ')']
# token types
err_t = 0       # invalid token
ident_t = 1     # Identifier
lit_t = 2       # Literal integer
op_t = 3        # Operator
assign_t = 4    # Assignment
bracket_t = 5   # Round Brackets


class Stack:
    """Implements a stack based on python list """
    def __init__(self):
        """ Build local stack list and item counter """
        self.stack_list = []
        self.stack_depth = 0

    def s_push(self, item):
        """Add an item to end of stack list """
        self.stack_list.append(item)
        self.stack_depth += 1

    def s_pop(self):
        """If not empty, remove and return the item at the end of the stack list.
        Otherwise, return None """
        if self.stack_depth > 0:
            self.stack_depth -= 1
            return self.stack_list.pop(-1)
        return None

    def s_peek(self):
        """Returns the item at the end of the stack list, without removing it.
        Return None if stack is empty """
        if self.stack_depth > 0:
            return self.stack_list[-1]
        return None

    def s_empty(self):
        if self.stack_depth == 0:
            return True
        return False


def remove_whitespace(text):
    s_line = ""
    for c in text:
        if c == ' ' or c == '\t':
            continue
        else:
            s_line = s_line + c
    return s_line


def check_repeat_operators(text):
    """ Odd numbers of Consecutive repeated '-' signs are replaced with a single '+' sign,
    and multiple consecutive '+' signs are reduced to a single '+'.
    Embedded whitespace is then reduced to a single space.
    Two or more consecutive '*' or '/' signs cause an 'Invalid expression' error.
    Returns the reduced text string, or None if an 'Invalid Expression' occurs."""
    if len(text) < 2:   # just return if the string is too short for any repeats
        return text
    ltext = text.replace("--", "+")         # change double-negative into positive
    while not ltext.find("++") == -1:
        ltext = ltext.replace("++", "+")    # shrink repeated pluses to one
    ltext = ltext.replace("+-", "-")        # fix any triple negatives
    ltext = ltext.replace("-+", "-")
    ltext = ltext.replace("\t", " ")        # change TABs into SPACES
    while not ltext.find("  ") == -1:       # compress multiple spaces to a single space
        ltext = ltext.replace("  ", " ")
    if not ltext.find("**") == -1:          # too many * signs is Invalid
        print('Invalid expression')
        return None
    if not ltext.find("//") == -1:          # too many / signs is also bad
        print('Invalid expression')
        return None
    return ltext


def get_next_token(text):
    """From the text provided, the end-position and type of the next token is returned as
    tuple(ttype, str), where ttype = 1 is identifier name, 2 is integer literal,
    3 is arithmetic operator, 4 is Assignment '=' and 0 is unrecognised/invalid.
    str is the token string.
    tlen is number of characters in token. ie slice position AFTER end of token """
    if len(text) < 1:
        return None
    ttype = 0
    tlen = 0
    if text[0].isalpha():
        ttype = 1
        for c in text:
            if c.isalpha():
                tlen += 1
            else:
                break
    elif text[0].isdigit():
        ttype = 2
        for c in text:
            if c.isdigit():
                tlen += 1
            else:
                break
    elif text[0] in operators:
        ttype = 3
        tlen = 1
    elif text[0] == '=':
        ttype = 4
        tlen = 1
    elif text[0] in brackets:
        ttype = 5
        tlen = 1
    else:
        tlen = 1
    return ttype, text[:tlen]


def calc_parse(text):
    t_list = []
    i = 0
    while i < len(text):
        if text[i].isspace():   # step over leading space
            if i < len(text):
                i += 1
        t_token = get_next_token(text[i:])
        t_list.append(t_token)
        i = i + len(t_token[1])
    return t_list


def fix_unary_minus(tokens):
    """handles a starting minus sign before an expression or an identifier.
    The unary minus is removed and value of following identifier or literal is negated.
    if it's just a minus sign only, or the following identifier does not exist
    then return a token list containing only an impossible identifier.
    Hopefully this will force an 'Invalid expression' error in calling code"""
    if tokens is None or len(tokens) < 1:
        return tokens
    t = tokens
    if t[0][1] == '-':              # unary minus found ?
        if len(t) < 2:              # without a following identifier...
            return [(ident_t, " ")]  # force invalid expression error
        if t[1][0] == ident_t:      # with a following identifier...
            if t[1][1] in variables:  # if it exists, negate it's value
                val = variables[t[1][1]]
                variables[t[1][1]] = 0 - val
                t.pop(0)            # remove the unary minus operator
            else:
                return [(ident_t, " ")]  # otherwise, force an invalid expressions error
        elif t[1][0] == lit_t:      # with a following literal
            tval = t[1][1]
            t[1] = (lit_t, '-' + tval)  # prepend the unary minus to the literal string
            t.pop(0)                # remove the unary minus operator
    return t


def higheq_precedence(t1, t2):
    """ t1 and t2 are operator tokens. If t1 is higher or equal precedence than t2, return True,
    otherwise, return False """
    if p_table[t1] >= p_table[t2]:
        return True
    return False


def prefix_to_postfix(tokens):
    """takes a token list postfix expression and returns the token list in postfix sequence"""
    if len(tokens) < 2:                     # not enough tokens to form an expression
        return tokens                       # return token list unchanged.
    s = Stack()     # Operator stack
    t = []          # output list of token tuples
    nesting = 0     # bracket pair counter
    for ttype, tval in tokens:              # scan the infix token list
        if ttype == ident_t or ttype == lit_t:
            t.append((ttype, tval))         # add operands to the postfix list
        elif tval == '(':
            s.s_push((ttype, tval))         # just push open bracket onto operator stack
            nesting += 1                    # bump the number of bracket pairs
        elif ttype == op_t:                 # got an operator...
            if s.s_empty() or s.s_peek()[1] in brackets:
                s.s_push((ttype, tval))     # push onto stack if starting or if ToS is a bracket
            elif higheq_precedence(s.s_peek()[1], tval):  # operator with prec. >= at ToS ?
                while not s.s_empty() and higheq_precedence(s.s_peek()[1], tval):
                    t.append(s.s_pop())     # transfer stack operator(s) to Postfix list
                s.s_push((ttype, tval))     # then push infix operator onto stack
            else:
                s.s_push((ttype, tval))     # otherwise, just stack the infix operator
        elif tval == ')':               # got a closing bracket...
            nesting -= 1                # reduce level of nested brackets.
            if nesting < 0:
                print("Invalid expression")  # too many closing brackets ??
                return None
            stype, sval = s.s_pop()     # move operators from stack to postfix list
            while not sval == '(':      # until an opening bracket is popped
                t.append((stype, sval))
                if not s.s_empty():
                    stype, sval = s.s_pop()
                else:
                    print("Invalid expression")  # stack exhausted ?? prefix syntax error
                    return None
        else:
            print("Invalid expression")     # not expected syntax ?? prefix error
            return None
    # after all tokens have been scanned...
    while not s.s_empty():                  # transfer remaining operator tokens
        t.append(s.s_pop())                 # to the postfix list
    if nesting:
        print("Invalid expression")         # unmatch pairs o f brackets
        return None
    return t                                # and return the postfix token list


def alu(op, v1, v2):
    """Perform arithmetic and return result"""
    if op == '+':           # ADD
        return v1 + v2
    elif op == '-':         # SUBTRACT
        return v1 - v2
    elif op == '*':         # MULTIPLY
        return v1 * v2
    elif op == '/':         # INTEGER DIVIDE
        return v2 and v1 // v2  # Avoid divide by zero error


def t_valuate(tokens):
    vs = Stack()        # local postfix operations stack
    pf_tokens = prefix_to_postfix(tokens)   # convert token list ot postfix notation
    if pf_tokens and not pf_tokens == []:   # skip if token list is None...
        for ttype, tval in pf_tokens:       # scan thru postfix token list
            if ttype == lit_t:              # stack a literal values
                vs.s_push(int(tval))
            elif ttype == ident_t:          # stack the value of an identifier
                if tval in variables.keys():
                    vs.s_push(variables[tval])
                else:
                    print("Invalid expression")  # bad identifier... Error
                    return None
            elif ttype == op_t:             # get operands from stack
                t2 = vs.s_pop()
                t1 = vs.s_pop()
                if not (t1 is None or t2 is None):   # if operands are present,
                    vs.s_push(alu(tval, t1, t2))  # do the calculation and stack the result
                else:
                    print('Invalid expression')  # missing operands are a problem!
                    return None
        return vs.s_pop()   # return the result
    return None             # or return nothing after error


# calculator.py starts here...
running = True
while running:
    line = ""
    while line == "":       # get an infix format line to calculate
        line = input()
    if line.startswith('/'):
        if line == '/exit':
            print("Bye!")
            running = False
            continue
        elif line == '/help':
            print('Smart Calculator obeys +, -, * and / with precedence for expressions in ()')
            continue
        else:
            print("Unknown command")
            continue
    fixed_line = check_repeat_operators(line.strip())   # clean up repeated operators and whitespace
    if fixed_line is None:
        continue                        # ignore an empty list after error
    line_tokens = calc_parse(fixed_line)  # reduce line to list of token tuples
    if line_tokens is None or len(line_tokens) < 1:
        continue                        # Just ignore an empty token list
    line_tokens = fix_unary_minus(line_tokens)  # process any starting unary minus
    if line_tokens[0][0] == ident_t:    # starting with a named variable
        if len(line_tokens) == 1:       # print value of solo variables
            if line_tokens[0][1] in variables:  # show value of exiting variable
                print(variables[line_tokens[0][1]])
            else:                       # or error if variable is undefined
                print('Unknown variable')
        else:
            if line_tokens[1][0] == assign_t:   # assignment?
                rhs = line_tokens[2:]
                variables[line_tokens[0][1]] = t_valuate(rhs)  # evaluate RHS & store variable
            else:
                result = t_valuate(line_tokens)  # evaluate the bare expressions
                if result is not None:  # and print the result
                    print(result)
    elif line_tokens[0][0] == lit_t:        # starting with a literal integer
        if len(line_tokens) == 1:           # print value of solo literal
            print(int(line_tokens[0][1]))
        else:
            result = t_valuate(line_tokens)  # evaluate it
            if result is not None:          # and print it
                print(result)
    else:
        if line_tokens[0][1] == '(':        # starts with an open bracket
            result = t_valuate(line_tokens)  # evaluate it
            if result is not None:          # and print it
                print(result)
        else:
            print('Invalid expression')  # bad expression
# print("end")
