import re

import constants
from MachineCommand import MachineCommand
from PostfixNotation import PostfixNotation
from program_blocks.ProgramBlock import ProgramBlock
from program_blocks.ProgramBlockElif import ProgramBlockElif
from program_blocks.ProgramBlockElse import ProgramBlockElse
from program_blocks.ProgramBlockFor import ProgramBlockFor
from program_blocks.ProgramBlockIf import ProgramBlockIf
from program_blocks.ProgramBlockMain import ProgramBlockMain
from program_blocks.ProgramBlockWhile import ProgramBlockWhile

program_blocks = [
    ProgramBlockMain,
    ProgramBlockIf,
    ProgramBlockElif,
    ProgramBlockElse,
    ProgramBlockFor,
    ProgramBlockWhile,
]


class Compiler:

    def __init__(self):
        self.register_count = 6
        self.temp_variables_reg_offset = 3
        self.temp_variables_reg_count = self.register_count - self.temp_variables_reg_offset

        self.next_var_index = self.register_count
        self.postfix_notation = PostfixNotation()

        self.variables = {}
        self.temp_variables = []

        self.regexps = {
            fr'input\(({constants.variable_regex})\)': self.input,
            fr'display\(({constants.var_val_regex})\)': self.display,
            fr'({constants.variable_regex})\s*=\s*(.*)': self.compile_value_assignment
        }

        self.temp_var_prefix = '__temp_var'

        for i in range(self.temp_variables_reg_count):
            temp_var = self.get_temp_var_by_index(i)
            self.variables[temp_var] = i + self.temp_variables_reg_offset
            self.temp_variables.append(temp_var)

        self.ALU_output_var = '__ALU_output'
        self.variables[self.ALU_output_var] = 0

    def compile_program(self, program):
        program_block = _split_program_to_blocks_by_indents(program)
        program_block = ProgramBlockMain('main', _combine_conditional_blocks(
            _combine_entry_commands_with_blocks(program_block)))
        machine_commands = self.program_block_to_machine_commands(program_block, 0, False)

        return machine_commands

    def program_block_to_machine_commands(self, program_block: ProgramBlock, offset, have_next_block):
        commands_in_block = []
        init_commands = program_block.init_machine_commands(self)

        for i, line in enumerate(program_block.block):
            if isinstance(line, str):
                commands_in_block += self.line_to_machine_commands(line)
            if isinstance(line, list):
                for j, block in enumerate(line):
                    commands_in_block += self.program_block_to_machine_commands(block,
                                                                                offset + len(init_commands) +
                                                                                program_block.entry_offset +
                                                                                len(commands_in_block),
                                                                                j < len(line) - 1)

        entry_commands, end_commands = program_block.entry_machine_commands(self, offset, len(commands_in_block),
                                                                            have_next_block)

        return init_commands + entry_commands + commands_in_block + end_commands

    def line_to_machine_commands(self, line):
        for reg, func in self.regexps.items():
            res = re.fullmatch(reg, line)
            if res:
                return func(*res.groups())
        raise Exception(f'Unresolved command "{line}"')

    def try_add_variable(self, var):
        if var not in self.variables:
            self.variables[var] = self.next_var_index
            self.next_var_index += 1
            return self.variables[var], True
        return self.variables[var], False

    def get_temp_var_by_index(self, index):
        return self.temp_var_prefix + str(index)

    def get_or_create_temp_var(self, index):
        temp_var = self.get_temp_var_by_index(index)
        address, result = self.try_add_variable(temp_var)
        if result:
            self.temp_variables.append(temp_var)
        return temp_var, result

    def compile_value_assignment(self, var, exp):
        address, _ = self.try_add_variable(var)

        commands = self.compile_math_expression(exp, address)

        return commands

    def compile_math_expression(self, exp, output_address):
        commands = []
        postfix_exp = self.postfix_notation.infix_to_postfix(exp)
        stack = []
        temp_var_index = 0

        def get_arg_from_stack(reg):
            arg = stack.pop()
            addr, cmd = self.load_to_reg(arg, reg)
            return addr, cmd, arg in self.temp_variables

        def is_cmd(a):
            return not (a is int or a.isdigit() or a in self.variables)

        for i, s in enumerate(postfix_exp):
            if not is_cmd(s):
                stack.append(s)
            else:
                if s in constants.one_seat_operation_to_machine_cmd:
                    machine_cmd = constants.one_seat_operation_to_machine_cmd[s]

                    addr0, cmd0, is_temp = get_arg_from_stack(1)
                    if cmd0:
                        commands.append(cmd0)
                    if is_temp:
                        temp_var_index -= 1

                    commands.append(MachineCommand.tokens_to_command([machine_cmd, addr0]))

                elif s in constants.two_seat_operation_to_machine_cmd:
                    machine_cmd = constants.two_seat_operation_to_machine_cmd[s]

                    addr0, cmd0, is_temp = get_arg_from_stack(1)
                    if cmd0:
                        commands.append(cmd0)
                    if is_temp:
                        temp_var_index -= 1

                    addr1, cmd1, is_temp = get_arg_from_stack(2)
                    if cmd1:
                        commands.append(cmd1)
                    if is_temp:
                        temp_var_index -= 1

                    commands.append(MachineCommand.tokens_to_command([machine_cmd, addr1, addr0]))

                if (i + 1 < len(postfix_exp) and is_cmd(postfix_exp[i + 1])) or \
                        (i + 2 < len(postfix_exp) and is_cmd(postfix_exp[i + 2]) and
                         s in constants.two_seat_operation_to_machine_cmd):
                    stack.append(self.ALU_output_var)
                elif i + 1 < len(postfix_exp):
                    temp_var, _ = self.get_or_create_temp_var(temp_var_index)
                    temp_var_index += 1
                    stack.append(temp_var)

                    cmd = self.move(0, self.variables[temp_var])
                    commands.append(cmd)

        if len(postfix_exp) == 1:
            cmd = self.move_or_put(stack.pop(), output_address)
        else:
            cmd = self.move(0, output_address)
        commands.append(cmd)

        return commands

    def load_to_reg(self, arg, reg):
        if reg <= 0 or reg >= self.register_count:
            raise Exception(f'Reg out of rage {reg}')

        if arg is int or arg.isdigit():
            return reg, self.put_value(arg, reg)

        address = self.variables[arg]
        if address < self.register_count:
            return address, None
        return reg, self.move(address, reg)

    def move_or_put(self, arg, address):
        if arg is int or arg.isdigit():
            return self.put_value(arg, address)
        else:
            return self.move(self.variables[arg], address)

    def move(self, address0, address1):
        command = MachineCommand.tokens_to_command(['mov', address0, address1])
        return command

    def put_value(self, val, address):
        command = MachineCommand.tokens_to_command(['put', val, address])
        return command

    def display(self, arg):
        return [self.move_or_put(arg, 1),
                MachineCommand(101, 2, 1)]

    def input(self, arg):
        return [MachineCommand(102, 1, self.variables[arg])]


def _count_indents(line):
    res = re.match(r'(\s*)(.*)\s*', line)
    return res.span(1)[1], res.group(2)


def _split_program_to_blocks_by_indents(program):
    program_block = []
    block_stack = [program_block]
    indent_stack = [0]
    for line in program:
        indent, line = _count_indents(line)
        while indent < indent_stack[-1]:
            block_stack.pop()
            indent_stack.pop()

        if indent == indent_stack[-1]:
            block_stack[-1].append(line)
        elif indent > indent_stack[-1]:
            new_block = [line]
            block_stack[-1].append(new_block)
            block_stack.append(new_block)
            indent_stack.append(indent)
        else:
            raise Exception(f"Something went wrong Indent {indent} CurIndent {indent_stack[-1]}")

    return program_block


def _combine_conditional_blocks(program_block):
    new_program_block = []

    for line in program_block:
        if not isinstance(line, ProgramBlock):
            new_program_block.append(line)
            continue

        if isinstance(line, ProgramBlockIf) or isinstance(line, ProgramBlockFor) or isinstance(line, ProgramBlockWhile):
            new_program_block.append([line])
        elif isinstance(line, ProgramBlockElse) or isinstance(line, ProgramBlockElif):
            new_program_block[-1].append(line)
        else:
            new_program_block.append(line)

    return new_program_block


def _combine_entry_commands_with_blocks(program_list):
    new_program_block = []

    for i, line in enumerate(program_list):
        if isinstance(line, list):
            continue

        program_block_class = _try_get_program_block_class(line)

        if program_block_class:
            processed_block = _combine_conditional_blocks(_combine_entry_commands_with_blocks(program_list[i + 1]))
            program_block = program_block_class(line, processed_block)
            new_program_block.append(program_block)
        else:
            new_program_block.append(line)

    return new_program_block


def _try_get_program_block_class(entry_command):
    for cls in program_blocks:
        if re.fullmatch(cls.regex, entry_command):
            return cls
    return None
