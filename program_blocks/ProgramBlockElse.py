from MachineCommand import MachineCommand
from program_blocks.ProgramBlock import ProgramBlock


class ProgramBlockElse(ProgramBlock):
    regex = r'else:'

    def __init__(self, entry_command, block):
        super().__init__(entry_command, block)

    @property
    def entry_offset(self):
        return 1

    def entry_machine_commands(self, compiler, memory_manager, offset, block_len, have_next_block):
        return [MachineCommand.jmp(offset + self.entry_offset + block_len)], []
