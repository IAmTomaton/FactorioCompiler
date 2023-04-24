machine_cmd_id_dict = {
    'put': (1, 1),
    'mov': (1, 2),

    'add': (2, 1),  # +
    'sub': (2, 2),  # -
    'mul': (2, 3),  # *
    'div': (2, 4),  # /
    'rem': (2, 5),  # %
    'pow': (2, 6),  # **
    'shl': (2, 7),  # <<
    'shr': (2, 8),  # >>
    'and': (2, 9),
    'or': (2, 10),
    'xor': (2, 11),

    'lth': (2, 12),  # <
    'gth': (2, 13),  # >
    'qe': (2, 14),   # ==
    'geth': (2, 15), # >=
    'leth': (2, 16), # <=
    'neq': (2, 17),  # !=
    'not': (2, 18),  # not

    'inc': (2, 19),  # + 1
    'dec': (2, 20),  # - 1

    'jmp': (3, 1),
    'jmpne0': (3, 2),
    'jmpg0': (3, 3),
    'jmpl0': (3, 4),
    'jmpe0': (3, 5),
    'jmpge0': (3, 6),
    'jmple0': (3, 7),
    'jmpne': (3, 8),
    'jmpg': (3, 9),
    'jmpl': (3, 10),
    'jmpe': (3, 11),
    'jmpge': (3, 12),
    'jmple': (3, 13),
}

two_seat_operation_to_machine_cmd = {
    '+': 'add',
    '-': 'sub',
    '*': 'mul',
    '/': 'div',
    '%': 'rem',
    '**': 'pow',
    '<<': 'shl',
    '>>': 'shr',
    'and': 'and',
    'or': 'or',
    'xor': 'xor',

    '>': 'gth',
    '<': 'lth',
    '==': 'qe',
    '>=': 'geth',
    '<=': 'leth',
    '!=': 'neq'
}

one_seat_operation_to_machine_cmd = {
    'not': 'not',
}

variable_regex = r'[a-zA-Z_][0-9a-zA-Z_]*'
var_val_regex = r'[0-9a-zA-Z_]+'
