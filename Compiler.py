import re

import constants
from MachineCommand import MachineCommand
from MemoryManager import MemoryManager
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

    def __init__(self, memory_manager):
        self.memory_manager = memory_manager
        self.postfix_notation = PostfixNotation()

        self.regexps = {
            fr'input\(({constants.variable_regex})\)': self.input,
            fr'display\(({constants.var_val_regex})\)': self.display,
            fr'({constants.variable_regex})\s*=\s*(.*)': self.compile_value_assignment
        }

    def compile_program(self, program):
        program_block = _split_program_to_blocks_by_indents(program)
        program_block = ProgramBlockMain('main', _combine_conditional_blocks(
            _combine_entry_commands_with_blocks(program_block)))
        machine_commands = self.program_block_to_machine_commands(program_block, 0, False)

        return machine_commands

    def program_block_to_machine_commands(self, program_block: ProgramBlock, offset, have_next_block):
        commands_in_block = []
        init_commands = program_block.init_machine_commands(self, self.memory_manager)

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

        entry_commands, end_commands = program_block.entry_machine_commands(self, self.memory_manager, offset,
                                                                            len(commands_in_block), have_next_block)

        return init_commands + entry_commands + commands_in_block + end_commands

    def line_to_machine_commands(self, line):
        for reg, func in self.regexps.items():
            res = re.fullmatch(reg, line)
            if res:
                return func(*res.groups())
        raise Exception(f'Unresolved command "{line}"')

    def compile_value_assignment(self, var, exp):
        address, _ = self.memory_manager.try_add_variable(var)

        commands = self.compile_math_expression(exp, address)

        return commands

    def compile_math_expression(self, exp, output_address):
        commands = []
        postfix_exp = self.postfix_notation.infix_to_postfix(exp)
        stack = []
        temp_var_index = 0

        def load_arg_from_stack(reg):
            nonlocal temp_var_index
            arg = stack.pop()
            addr, cmd = self.memory_manager.load_to_reg(arg, reg)
            if cmd:
                commands.append(cmd)
            if arg in self.memory_manager.temp_variables:
                temp_var_index -= 1
            return addr

        def is_cmd(a):
            return not (a is int or a.isdigit() or a in self.memory_manager.variables)

        for i, s in enumerate(postfix_exp):
            if not is_cmd(s):
                stack.append(s)
            else:
                if s in constants.one_seat_operation_to_machine_cmd:
                    machine_cmd = constants.one_seat_operation_to_machine_cmd[s]

                    addr0 = load_arg_from_stack(1)

                    commands.append(MachineCommand.tokens_to_command([machine_cmd, addr0]))

                elif s in constants.two_seat_operation_to_machine_cmd:
                    machine_cmd = constants.two_seat_operation_to_machine_cmd[s]

                    addr0 = load_arg_from_stack(1)
                    addr1 = load_arg_from_stack(2)

                    commands.append(MachineCommand.tokens_to_command([machine_cmd, addr1, addr0]))
                else:
                    raise Exception(f'Unknown math operation "{s}"')

                if (i + 1 < len(postfix_exp) and is_cmd(postfix_exp[i + 1])) or \
                        (i + 2 < len(postfix_exp) and is_cmd(postfix_exp[i + 2]) and
                         s in constants.two_seat_operation_to_machine_cmd):
                    stack.append(self.memory_manager.ALU_output_var)
                elif i + 1 < len(postfix_exp):
                    temp_var, _ = self.memory_manager.get_or_create_temp_var(temp_var_index)
                    temp_var_index += 1
                    stack.append(temp_var)

                    cmd = MachineCommand.move(0, self.memory_manager.variables[temp_var])
                    commands.append(cmd)

        if len(postfix_exp) == 1:
            cmd = self.memory_manager.move_or_put(stack.pop(), output_address)
        else:
            cmd = MachineCommand.move(0, output_address)
        commands.append(cmd)

        return commands

    def display(self, arg):
        return [self.memory_manager.move_or_put(arg, 1),
                MachineCommand(101, 2, 1)]

    def input(self, arg):
        return [MachineCommand(102, 1, self.memory_manager.variables[arg])]


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
