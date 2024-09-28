# python implementation for parsing math expressions given in the form of strings

import doctest

def tokenize(string):
    """
    Given a string, return a list of the separate tokens of the string
    """
    modified_str = ""
    for char in string:
        if char == "(":
            modified_str += char + " "
        elif char == ")":
            modified_str += " " + char
        else:
            modified_str += char
    modified_str = modified_str.split(" ")
    return [char for char in modified_str if char != ""]


def create_instance(left_exp, right_exp, operator):
    """
    Helper function to return instance corresponding to operator 
    passed in. 
    """
    if operator == "+":
        return Add(left_exp, right_exp)
    elif operator == "-":
        return Sub(left_exp, right_exp)
    elif operator == "*":
        return Mul(left_exp, right_exp)
    else:
        return Div(left_exp, right_exp)


def parse(tokens):
    """
    Given a list of tokens, return python-readable expression
    """
    def parse_expression(index):
        if tokens[index].isalpha():
            return (Var(tokens[index]), index + 1)
        elif tokens[index] == "(":
            left_sub, left_i = parse_expression(index + 1)
            right_sub, right_i = parse_expression(left_i + 1)
            return (create_instance(left_sub, right_sub, tokens[left_i]), right_i + 1)
        else:
            if "-" in tokens[index]:
                return (Num(-float(tokens[index][1:])), index + 1)
            return (Num(float(tokens[index])), index + 1)

    parsed_expression, _ = parse_expression(0)
    return parsed_expression


def expression(string):
    """
    Given a string, return a Python-readable expressio
    """
    tokens = tokenize(string)
    print(tokens)
    return parse(tokens)


class Symbol:
    """
    Object that represents any symbolic expression
    ex. x + 2*y - 3*z
    """
    precedence = float("inf")
    wrap_right_at_same_precedence = False

    def __add__(self, other):
        return Add(self, other)

    def __radd__(self, other):
        return Add(other, self)

    def __sub__(self, other):
        return Sub(self, other)

    def __rsub__(self, other):
        return Sub(other, self)

    def __mul__(self, other):
        return Mul(self, other)

    def __rmul__(self, other):
        return Mul(other, self)

    def __truediv__(self, other):
        return Div(self, other)

    def __rtruediv__(self, other):
        return Div(other, self)

    def __eq__(self, other):
        if not isinstance(self, type(other)):
            return False
        if isinstance(self, Var):
            return self.__str__() == other.__str__()
        if isinstance(self, Num):
            return self.eval() == other.eval()
        return self.left.__eq__(other.left) and self.right.__eq__(other.right)


class Var(Symbol):
    """
    Object that represents a single variable
    ex. x, y, A, z
    """
    def __init__(self, n):
        """
        Initializer.  Store an instance variable called `name`, containing the
        value passed in to the initializer.
        """
        self.name = n

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"Var('{self.name}')"

    def eval(self, mapping):
        if str(self) in mapping:
            return mapping[str(self)]
        else:
            raise NameError

    def deriv(self, wrespect):
        if wrespect == str(self):
            return Num(1)
        return Num(0)

    def simplify(self):
        return self


class Num(Symbol):
    """
    Class that represents a number
    ex. 52, -11, 0.5
    """
    def __init__(self, n):
        """
        Initializer.  Store an instance variable called `n`, containing the
        value passed in to the initializer.
        """
        self.n = n

    def __str__(self):
        return str(self.n)

    def __repr__(self):
        return f"Num({self.n})"

    def eval(self, _=0):
        return self.n

    def deriv(self, _):
        return Num(0)

    def simplify(self):
        return self


def convert_type(obj):
    """
    Convert an int or float to a Num object or convert a str
    to a Var object 
    """
    if isinstance(obj, (int, float)):
        return Num(obj)
    elif isinstance(obj, str):
        return Var(obj)
    return obj


class BinOp(Symbol):
    """
    Superclass that represents a binary operation.
    """
    def __init__(self, left, right):
        self.left = convert_type(left)
        self.right = convert_type(right)

    def __str__(self):
        str_left = self.left.__str__()
        str_right = self.right.__str__()
        if self.left.precedence < self.precedence:
            str_left = "(" + str_left + ")"
        if self.right.precedence < self.precedence or (
            self.wrap_right_at_same_precedence
            and self.precedence == self.right.precedence
        ):
            str_right = "(" + str_right + ")"

        return str_left + " " + self.operation + " " + str_right

    def __repr__(self):
        return (
            str(self.__class__.__name__)
            + "("
            + self.left.__repr__()
            + ", "
            + self.right.__repr__()
            + ")"
        )

    def simplify(self):
        simplified_left = self.left.simplify()
        simplified_right = self.right.simplify()
        if isinstance(simplified_left, Num) and isinstance(simplified_right, Num):
            return self.num_eval(simplified_left, simplified_right)
        return self.simplify_helper(simplified_left, simplified_right)


class Add(BinOp):
    """
    Class objects represent adding two objects together 
    """
    operation = "+"
    precedence = 1

    def eval(self, mapping):
        return self.left.eval(mapping) + self.right.eval(mapping)

    def num_eval(self, left, right):
        return Num(left.n + right.n)

    def deriv(self, wrespect):
        return Add(self.left.deriv(wrespect), self.right.deriv(wrespect))

    def simplify_helper(self, left, right):
        if left == Num(0) or right == Num(0):
            if left == Num(0):
                return right
            return left
        return Add(left, right)


class Sub(BinOp):
    """
    Class objects represent subtracting the right object from the left
    """
    wrap_right_at_same_precedence = True
    operation = "-"
    precedence = 1

    def eval(self, mapping):
        return self.left.eval(mapping) - self.right.eval(mapping)

    def num_eval(self, left, right):
        return Num(left.n - right.n)

    def deriv(self, wrespect):
        return Sub(self.left.deriv(wrespect), self.right.deriv(wrespect))

    def simplify_helper(self, left, right):
        if right == Num(0):
            return left
        return Sub(left, right)


class Mul(BinOp):
    """
    Class objects represent multiplying two objects together
    """
    operation = "*"
    precedence = 2

    def eval(self, mapping):
        return self.left.eval(mapping) * self.right.eval(mapping)

    def num_eval(self, left, right):
        return Num(left.n * right.n)

    def deriv(self, wrespect):
        return Add(
            Mul(self.left, self.right.deriv(wrespect)),
            Mul(self.right, self.left.deriv(wrespect)),
        )

    def simplify_helper(self, left, right):
        if left == Num(0) or right == Num(0):
            return Num(0)
        if left == Num(1) or right == Num(1):
            if left == Num(1):
                return right
            return left
        return Mul(left, right)


class Div(BinOp):
    """
    Class objects represent dividing the right object from the left
    """
    wrap_right_at_same_precedence = True
    operation = "/"
    precedence = 2

    def eval(self, mapping):
        return self.left.eval(mapping) / self.right.eval(mapping)

    def num_eval(self, left, right):
        return Num(left.n / right.n)

    def deriv(self, wrespect):
        return Div(
            Sub(
                Mul(self.right, self.left.deriv(wrespect)),
                Mul(self.left, self.right.deriv(wrespect)),
            ),
            Mul(self.right, self.right),
        )

    def simplify_helper(self, left, right):
        if left == Num(0):
            return Num(0)
        if right == Num(1):
            return left
        return Div(left, right)


if __name__ == "__main__":
    doctest.testmod()
