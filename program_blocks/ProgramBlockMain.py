from program_blocks.ProgramBlock import ProgramBlock


class ProgramBlockMain(ProgramBlock):
    regex = r'main'

    def __init__(self, entry_command, block):
        super().__init__(entry_command, block)

    @property
    def entry_offset(self):
        return 0

    def entry_machine_commands(self, compiler, offset, block_len, have_next_block):
        return [], []
