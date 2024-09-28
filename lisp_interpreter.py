# this is a simplified interpreter for LISP

#!/usr/bin/env python3
import sys

sys.setrecursionlimit(20_000)

def variable_viability(variable):
    if (
        isinstance(variable, str)
        and "(" not in variable
        and ")" not in variable
        and " " not in variable
    ):
        return
    raise SyntaxError("Variable name not viable")


class Frame:
    """
    Creates object associated with frames (ex. global frames) in Scheme
    """

    def __init__(self, parent, variables):
        self.parent = parent
        self.variables = variables

    def __getitem__(self, variable):
        if variable in self.variables:
            return self.variables[variable]
        else:
            try:
                return self.parent[variable]
            except (KeyError, TypeError) as exc:
                raise SchemeNameError from exc

    def __setitem__(self, variable, value):
        variable_viability(variable)
        self.variables[variable] = value

    def __contains__(self, variable):
        try:
            _ = self[variable]
            return True
        except SchemeNameError:
            return False


def make_initial_frame():
    return Frame(Frame(None, scheme_builtins), {})


def create_variable_dict(parameters, arguments):
    variable_dict = {}
    for i, parameter in enumerate(parameters):
        variable_dict[parameter] = arguments[i]
    return variable_dict


class Function:
    """
    Create object corresponding to a function in Scheme
    """

    def __init__(self, parameters, body, enclosing_frame):
        self.parameters = parameters
        self.body = body
        self.enclosing_frame = enclosing_frame

    def __call__(self, arguments):
        if len(arguments) != len(self.parameters):
            raise SchemeEvaluationError
        function_frame = Frame(
            self.enclosing_frame, create_variable_dict(self.parameters, arguments)
        )
        return evaluate(self.body, function_frame)


class Pair:
    def __init__(self, car, cdr):
        self.car = car
        self.cdr = cdr

    def __str__(self):
        return "Pair: " + str(self.car) + " " + str(self.cdr)


#############################
# Scheme-related Exceptions #
#############################


class SchemeError(Exception):
    """
    A type of exception to be raised if there is an error with a Scheme
    program.  Should never be raised directly; rather, subclasses should be
    raised.
    """

    pass


class SchemeSyntaxError(SchemeError):
    """
    Exception to be raised when trying to evaluate a malformed expression.
    """

    pass


class SchemeNameError(SchemeError):
    """
    Exception to be raised when looking up a name that has not been defined.
    """

    pass


class SchemeEvaluationError(SchemeError):
    """
    Exception to be raised if there is an error during evaluation other than a
    SchemeNameError.
    """

    pass


############################
# Tokenization and Parsing #
############################


def number_or_symbol(value):
    """
    Helper function: given a string, convert it to an integer or a float if
    possible; otherwise, return the string itself

    >>> number_or_symbol('8')
    8
    >>> number_or_symbol('-5.32')
    -5.32
    >>> number_or_symbol('1.2.3.4')
    '1.2.3.4'
    >>> number_or_symbol('x')
    'x'
    """
    try:
        return int(value)
    except ValueError:
        try:
            return float(value)
        except ValueError:
            return value


def modify_string(string):
    """
    Helper function for handling comments and new lines in code
    """
    modified_str = ""
    comment = False
    for char in string:
        if char == ";":
            comment = True
            continue
        if comment:
            if char == "\n":
                comment = False
            continue
        modified_str += char
    return modified_str.replace("\n", " ")


def tokenize(source):
    """
    Splits an input string into meaningful tokens (left parens, right parens,
    other whitespace-separated values).  Returns a list of strings.

    Arguments:
        source (str): a string containing the source code of a Scheme
                      expression
    """
    modified_str = ""
    for char in modify_string(source):
        if char == "(":
            modified_str += char + " "
        elif char == ")":
            modified_str += " " + char + " "
        else:
            modified_str += char
    modified_str = modified_str.split(" ")
    return [char for char in modified_str if char != ""]


def isvalid(tokens):
    """
    Returns True if the input is valid in Scheme syntax, else False
    """
    if len(tokens) != 1 and (tokens[0] != "(" or tokens[-1] != ")"):
        return False
    open_count = 0
    close_count = 0
    for element in tokens:
        if element == "(":
            open_count += 1
        if element == ")":
            close_count += 1
    return open_count == close_count


def parse(tokens):
    """
    Parses a list of tokens, constructing a representation where:
        * symbols are represented as Python strings
        * numbers are represented as Python ints or floats
        * S-expressions are represented as Python lists

    Arguments:
        tokens (list): a list of strings representing tokens
    """
    if not isvalid(tokens):
        raise SchemeSyntaxError
    parse_list = []

    def parse_expression(index):
        if tokens[index] == "(":
            s_expression = []
            i = index
            while True:
                i += 1
                if tokens[i] == "(":
                    inner_expr, end_i = parse_expression(i)
                    s_expression.append(inner_expr)
                    i = end_i
                elif tokens[i] == ")":
                    break
                else:
                    s_expression.append(number_or_symbol(tokens[i]))
            return s_expression, i
        else:
            parse_list.append(number_or_symbol(tokens[index]))
            return (number_or_symbol(tokens[index]), index + 1)

    final_expr, _ = parse_expression(0)
    parse_list = final_expr
    return parse_list


######################
# Built-in Functions #
######################


def multiply(num):
    product = num[0]
    for element in num[1:]:
        product *= element
    return product


def divide(num):
    if not num:
        raise SchemeEvaluationError
    elif len(num) == 1:
        return 1 / num[0]
    else:
        result = num[0]
        for element in num[1:]:
            result /= element
        return result


def equal(num):
    for i in num[1:]:
        if num[0] != i:
            return False
    return True


def greater(num):
    for i, val in enumerate(num[:-1]):
        if val <= num[i + 1]:
            return False
    return True


def greater_equal(num):
    for i, val in enumerate(num[:-1]):
        if val < num[i + 1]:
            return False
    return True


def less(num):
    for i, val in enumerate(num[:-1]):
        if val >= num[i + 1]:
            return False
    return True


def less_equal(num):
    for i, val in enumerate(num[:-1]):
        if val > num[i + 1]:
            return False
    return True


def negate(expression):
    if len(expression) != 1:
        raise SchemeEvaluationError
    else:
        if expression[0]:
            return False
        return True


def create_con(inp):
    if len(inp) != 2:
        raise SchemeEvaluationError
    return Pair(inp[0], inp[1])


def get_car(cons_cell):
    if len(cons_cell) != 1 or not isinstance(cons_cell[0], Pair):
        raise SchemeEvaluationError
    return cons_cell[0].car


def get_cdr(cons_cell):
    if len(cons_cell) != 1 or not isinstance(cons_cell[0], Pair):
        raise SchemeEvaluationError
    return cons_cell[0].cdr


def type_check_list(inp):
    if len(inp) != 1:
        raise SchemeEvaluationError
    return [] in inp or (isinstance(inp[0], Pair) and (type_check_list([inp[0].cdr])))


def list_length(ll):
    if not type_check_list(ll):
        raise SchemeEvaluationError

    def length_helper(ll, sofar=0):
        if not ll:
            return sofar
        return length_helper(ll.cdr, sofar + 1)

    return length_helper(ll[0])


def list_reference(inp):
    """
    Given an input that contains a Scheme list and index, return
    the value of the list at that index
    """
    if len(inp) != 2:
        raise SchemeEvaluationError
    ll, index = inp[0], inp[1]
    if isinstance(ll, Pair) and not type_check_list([ll.cdr]):
        if index == 0:
            return ll.car
        raise SchemeEvaluationError
    if (
        not type_check_list([ll])
        or not isinstance(index, int)
        or list_length([ll]) <= index
    ):
        raise SchemeEvaluationError

    def ref_helper(linked, i):
        if i == index:
            return linked.car
        return ref_helper(linked.cdr, i + 1)

    return ref_helper(ll, 0)


def all_lists(lists):
    for elt in lists:
        if not type_check_list([elt]):
            return False
    return True


def solo_list_extraction(elt):
    """
    Given a parsed and tokenized representation of a list, extract
    values and return as a Python list.
    """
    list_elements = []

    def extraction_helper(linked):
        if not linked:
            return None
        list_elements.append(linked.car)
        return extraction_helper(linked.cdr)

    extraction_helper(elt)
    return list_elements


def concatenate_list(list_elts):
    if not list_elts:
        return []
    return Pair(list_elts[0], concatenate_list(list_elts[1:]))


def append(lists):
    if not all_lists(lists):
        raise SchemeEvaluationError
    list_elts = []
    for elt in lists:
        list_elts += solo_list_extraction(elt)
    return concatenate_list(list_elts)


scheme_builtins = {
    "+": sum,
    "-": lambda args: -args[0] if len(args) == 1 else (args[0] - sum(args[1:])),
    "*": multiply,
    "/": divide,
    "equal?": equal,
    ">": greater,
    ">=": greater_equal,
    "<": less,
    "<=": less_equal,
    "not": negate,
    "#t": True,
    "#f": False,
    "car": get_car,
    "cdr": get_cdr,
    "()": [],
    "list?": type_check_list,
    "cons": create_con,
    "length": list_length,
    "list-ref": list_reference,
    "append": append,
}


##############
# Evaluation #
##############


def simplify_non_list(tree, frame):
    if isinstance(tree, (int, float)):
        return tree
    else:
        return frame[tree]


def evaluate_and(tree, frame):
    for expression in tree:
        if not evaluate(expression, frame):
            return False
    return True


def evaluate_or(tree, frame):
    for expression in tree:
        if evaluate(expression, frame):
            return True
    return False


def evaluate_conditional(tree, frame):
    if evaluate(tree[1], frame):
        return evaluate(tree[2], frame)
    return evaluate(tree[3], frame)


def create_linked_list(tree, frame):
    if not tree:
        return []
    return Pair(evaluate(tree[0], frame), create_linked_list(tree[1:], frame))


def delete_variables(tree, frame):
    if len(tree) != 1:
        raise SchemeEvaluationError
    if tree[0] in frame.variables:
        corresponding_value = frame.variables[tree[0]]
        del frame.variables[tree[0]]
        return corresponding_value
    else:
        raise SchemeNameError


def evaluate_let(tree, frame):
    binding_dict = {}
    for binding in tree[0]:
        binding_dict[binding[0]] = evaluate(binding[1], frame)
    f1 = Frame(frame, binding_dict)
    return evaluate(tree[1], f1)


def evaluate_set(var, exp, frame):
    if var in frame.variables:
        frame.variables[var] = exp
    elif frame.parent is not None:
        evaluate_set(var, exp, frame.parent)
    else:
        raise SchemeNameError


def evaluate(tree, frame=Frame(None, scheme_builtins)):
    """
    Evaluate the given syntax tree according to the rules of the Scheme
    language.

    Arguments:
        tree (type varies): a fully parsed expression, as the output from the
                            parse function
    """
    if not isinstance(tree, (list)):
        return simplify_non_list(tree, frame)
    if not tree:
        return []
    if tree[0] == "define":
        if isinstance(tree[1], list):
            implicit_func = evaluate(["lambda", tree[1][1:], tree[2]], frame)
            frame[tree[1][0]] = implicit_func
            return frame[tree[1][0]]
        else:
            frame[tree[1]] = evaluate(tree[2], frame)
            return frame[tree[1]]
    if tree[0] == "cons":
        if len(tree[1:]) != 2:
            raise SchemeEvaluationError
        if not tree[2]:
            return Pair(tree[1], [])
        return Pair(evaluate(tree[1], frame), evaluate(tree[2], frame))
    if tree[0] == "begin":
        for inp in tree[1:-1]:
            evaluate(inp, frame)
        return evaluate(tree[-1], frame)
    if tree[0] == "del":
        return delete_variables(tree[1:], frame)
    if tree[0] == "let":
        if len(tree) != 3:
            raise SchemeEvaluationError
        return evaluate_let(tree[1:], frame)
    if tree[0] == "set!":
        if len(tree) != 3:
            raise SchemeEvaluationError
        exp = evaluate(tree[2], frame)
        evaluate_set(tree[1], exp, frame)
        return exp
    if tree[0] == "list":
        return create_linked_list(tree[1:], frame)
    if tree[0] == "lambda":
        return Function(tree[1], tree[2], frame)
    if tree[0] == "and":
        return evaluate_and(tree[1:], frame)
    if tree[0] == "or":
        return evaluate_or(tree[1:], frame)
    if tree[0] == "if":
        return evaluate_conditional(tree, frame)
    evaluated_tree = evaluate(tree[0], frame)
    if not callable(evaluated_tree):
        raise SchemeEvaluationError
    arguments = [evaluate(element, frame) for element in tree[1:]]
    return evaluated_tree(arguments)


def evaluate_file(file_name, frame=Frame(None, scheme_builtins)):
    with open(file_name, "r") as file:
        file_contents = file.read()
    return evaluate(parse(tokenize(file_contents)), frame)


def setup_command_line():
    global_frame = Frame(None, scheme_builtins)
    for file in sys.argv[1:]:
        evaluate_file(file, global_frame)
    return global_frame


if __name__ == "__main__":
    pass
    import os

    sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
    import schemerepl

    schemerepl.SchemeREPL(
        sys.modules[__name__],
        use_frames=True,
        verbose=True,
        global_frame=setup_command_line(),
    ).cmdloop()
