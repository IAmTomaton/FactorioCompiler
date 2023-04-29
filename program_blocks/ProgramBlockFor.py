import re

from MachineCommand import MachineCommand
from program_blocks.ProgramBlock import ProgramBlock


class ProgramBlockFor(ProgramBlock):
    regex = r'for (\S\S*) in range\((.*)\):'
    end_prefix = '__end_range_'

    def __init__(self, entry_command, block):
        super().__init__(entry_command, block)

    @property
    def entry_offset(self):
        return 3

    @property
    def end_offset(self):
        return 4

    def init_machine_commands(self, compiler, memory_manager):
        i_var, exp = re.fullmatch(self.regex, self.entry_command).groups()

        self.i_var_address, _ = memory_manager.try_add_variable(i_var)
        i_init_command = MachineCommand.put(0, self.i_var_address)

        end_var = self.end_prefix + i_var
        self.end_var_address, _ = memory_manager.try_add_variable(end_var)
        exp_commands = compiler.compile_math_expression(exp, self.end_var_address)

        commands = [i_init_command] + exp_commands

        self.init_len = len(commands)

        return commands

    def entry_machine_commands(self, compiler, memory_manager, offset, block_len, have_next_block):
        check_commands = [
            MachineCommand.move(self.i_var_address, 1),
            MachineCommand.move(self.end_var_address, 2),
            MachineCommand.jmp_if_greater_or_eq_than(1, 2, offset + self.init_len + self.entry_offset + block_len +
                                                     self.end_offset)
        ]

        end_commands = [
            MachineCommand.move(self.i_var_address, 1),
            MachineCommand.tokens_to_command(['inc', 1]),
            MachineCommand.move(0, self.i_var_address),
            MachineCommand.jmp(offset + self.init_len)
        ]

        return check_commands, end_commands
