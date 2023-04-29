import re

from MachineCommand import MachineCommand
from program_blocks.ProgramBlock import ProgramBlock


class ProgramBlockIf(ProgramBlock):
    regex = r'if (.*):'

    def __init__(self, entry_command, block):
        super().__init__(entry_command, block)

    @property
    def entry_offset(self):
        return 2

    def entry_machine_commands(self, compiler, memory_manager, offset, block_len, have_next_block):
        exp = re.fullmatch(self.regex, self.entry_command).groups()[0]

        exp_commands = compiler.compile_math_expression(exp, 1)

        entry_commands = [
            MachineCommand.jmp_if_not_eq_0(1, offset + len(exp_commands) + self.entry_offset),
            MachineCommand.jmp(offset + len(exp_commands) + self.entry_offset + block_len + have_next_block),
        ]
        return exp_commands + entry_commands, []
