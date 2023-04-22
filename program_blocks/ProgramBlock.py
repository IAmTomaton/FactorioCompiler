class ProgramBlock:

    def __init__(self, entry_command, block):
        self.entry_command = entry_command
        self.block = block

    @property
    def entry_offset(self):
        return 0

    @property
    def end_offset(self):
        return 0

    def entry_machine_commands(self, compiler, offset, block_len, have_next_block):
        return [], []

    def init_machine_commands(self, compiler):
        return []
