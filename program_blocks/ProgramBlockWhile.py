import re

from MachineCommand import MachineCommand
from program_blocks.ProgramBlock import ProgramBlock


class ProgramBlockWhile(ProgramBlock):
    regex = r'while (.*):'
    end_prefix = '__end_range_'

    def __init__(self, entry_command, block):
        super().__init__(entry_command, block)

    @property
    def entry_offset(self):
        return 1

    @property
    def end_offset(self):
        return 1

    def init_machine_commands(self, compiler):
        exp = re.fullmatch(self.regex, self.entry_command).groups()[0]

        exp_commands = compiler.compile_math_expression(exp, 1)

        self.init_len = len(exp_commands)

        return exp_commands

    def entry_machine_commands(self, compiler, offset, block_len, have_next_block):
        check_commands = [
            MachineCommand.jmp_if_eq_0(1, offset + self.init_len + self.entry_offset + block_len + self.end_offset)
        ]

        end_commands = [
            MachineCommand.jmp(offset)
        ]

        return check_commands, end_commands
