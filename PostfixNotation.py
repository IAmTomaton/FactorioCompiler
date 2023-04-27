import re


class PostfixNotation:

    def __init__(self):
        self.precedence = {
            '(': -1,
            ')': -1,
            'xor': 0,
            'or': 1,
            'and': 2,
            'not': 3,
            '==': 4,
            '!=': 4,
            '>=': 4,
            '<=': 4,
            '|': 5,
            '^': 6,
            '&': 7,
            '<<': 8,
            '>>': 8,
            '<': 4,
            '>': 4,
            '+': 9,
            '-': 9,
            '*': 10,
            '/': 10,
            '%': 10,
            '~': 11,
            '->': 11,
            '**': 12,
        }

    def get_operators(self):
        return self.precedence.keys()

    def get_regex(self):
        operators = list(map(_operator_to_reg, self.get_operators()))
        return r'|'.join(operators) + r'|[a-zA-Z_][0-9a-zA-Z_]*|\d+'

    def is_operand(self, ch):
        return ch not in self.precedence

    def infix_to_postfix(self, exp):
        array = []
        output = []

        exp = re.findall(self.get_regex(), exp)

        for i in exp:
            if i == '(':
                array.append(i)
            elif i == ')':
                while array and array[-1] != '(':
                    a = array.pop()
                    output.append(a)
                array.pop()
            elif self.is_operand(i):
                output.append(i)
            else:
                while array and self.precedence[i] <= self.precedence[array[-1]]:
                    output.append(array.pop())
                array.append(i)

        while array:
            output.append(array.pop())

        return output


def _operator_to_reg(op):
    conversion = {
        '**': r'\*\*',
        '*': r'\*',
        '+': r'\+',
        '/': r'\/',
        '^': r'\^',
        '|': r'\|',
        '(': r'\(',
        ')': r'\)',
    }

    if op in conversion:
        return conversion[op]
    return op
