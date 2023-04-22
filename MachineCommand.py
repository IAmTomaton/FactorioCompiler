import string

from constants import machine_cmd_id_dict


class MachineCommand:
    signals_per_command = 5

    signals_names = []

    for i in range(0, 10):
        signals_names.append(f'signal-{i}')

    for i in string.ascii_uppercase[:10]:
        signals_names.append(f'signal-{i}')

    max_commands_in_combinator = len(signals_names) // signals_per_command

    def __init__(self, unit, cmd, arg0=None, arg1=None, arg2=None):
        self.unit = unit
        self.cmd = cmd
        self.arg0 = arg0
        self.arg1 = arg1
        self.arg2 = arg2

    @staticmethod
    def tokens_to_command(tokens):
        cmd = tokens[0]
        return MachineCommand(*machine_cmd_id_dict[cmd], *tokens[1:])

    def to_combinator(self, entity_number, position):
        signals = [
            {'signal': {'type': 'virtual', 'name': 'signal-U'}, 'count': self.unit, 'index': 1},
            {'signal': {'type': 'virtual', 'name': 'signal-C'}, 'count': self.cmd, 'index': 2},
        ]
        if self.arg0 is not None:
            signals.append({'signal': {'type': 'virtual', 'name': 'signal-0'}, 'count': self.arg0, 'index': 3})
        if self.arg1 is not None:
            signals.append({'signal': {'type': 'virtual', 'name': 'signal-1'}, 'count': self.arg1, 'index': 4})
        if self.arg2 is not None:
            signals.append({'signal': {'type': 'virtual', 'name': 'signal-2'}, 'count': self.arg2, 'index': 5})
        return {
            'entity_number': entity_number,
            'name': 'constant-combinator',
            'position': position,
            'direction': 2,
            'control_behavior': {'filters': signals}
        }

    @staticmethod
    def to_dense_combinator(commands, entity_number, position):
        if len(commands) * MachineCommand.signals_per_command > len(MachineCommand.signals_names):
            raise Exception(f'You cannot pack {len(commands)} commands of {MachineCommand.signals_per_command} signals '
                            f'({len(commands) * MachineCommand.signals_per_command} in total) using len(signals) signals')

        signals = []
        for i, command in enumerate(commands):
            signals_for_command = MachineCommand.signals_names[i * MachineCommand.signals_per_command:
                                                               (i + 1) * MachineCommand.signals_per_command]

            signals.append(
                {'signal': {'type': 'virtual', 'name': signals_for_command[0]}, 'count': command.unit,
                 'index': i * len(signals_for_command) + 1})
            signals.append(
                {'signal': {'type': 'virtual', 'name': signals_for_command[1]}, 'count': command.cmd,
                 'index': i * len(signals_for_command) + 2})
            if command.arg0 is not None:
                signals.append(
                    {'signal': {'type': 'virtual', 'name': signals_for_command[2]}, 'count': command.arg0,
                     'index': i * len(signals_for_command) + 3})
            if command.arg1 is not None:
                signals.append(
                    {'signal': {'type': 'virtual', 'name': signals_for_command[3]}, 'count': command.arg1,
                     'index': i * len(signals_for_command) + 4})
            if command.arg2 is not None:
                signals.append(
                    {'signal': {'type': 'virtual', 'name': signals_for_command[4]}, 'count': command.arg2,
                     'index': i * len(signals_for_command) + 5})
        return {
            'entity_number': entity_number,
            'name': 'constant-combinator',
            'position': position,
            'direction': 2,
            'control_behavior': {'filters': signals}
        }

    def __str__(self):
        return f"unit: {self.unit} cmd: {self.cmd} " \
               f"arg0: {'_' if self.arg0 is None else self.arg0} " \
               f"arg1: {'_' if self.arg1 is None else self.arg1} " \
               f"arg2: {'_' if self.arg2 is None else self.arg2}"

    def __repr__(self):
        return self.__str__()

    @staticmethod
    def jmp(index):
        return MachineCommand(*machine_cmd_id_dict['jmp'], arg2=index)

    @staticmethod
    def jmp_if_not_eq_0(arg, index):
        return MachineCommand(*machine_cmd_id_dict['jmpne0'], arg0=arg, arg2=index)

    @staticmethod
    def jmp_if_eq_0(arg, index):
        return MachineCommand(*machine_cmd_id_dict['jmpe0'], arg0=arg, arg2=index)

    @staticmethod
    def jmp_if_not_eq(arg0, arg1, index):
        return MachineCommand(*machine_cmd_id_dict['jmpne'], arg0=arg0, arg1=arg1, arg2=index)

    @staticmethod
    def jmp_if_eq(arg0, arg1, index):
        return MachineCommand(*machine_cmd_id_dict['jmpe'], arg0=arg0, arg1=arg1, arg2=index)

    @staticmethod
    def jmp_if_less_than(arg0, arg1, index):
        return MachineCommand(*machine_cmd_id_dict['jmpl'], arg0=arg0, arg1=arg1, arg2=index)

    @staticmethod
    def jmp_if_greater_than(arg0, arg1, index):
        return MachineCommand(*machine_cmd_id_dict['jmpg'], arg0=arg0, arg1=arg1, arg2=index)

    @staticmethod
    def jmp_if_less_or_eq_than(arg0, arg1, index):
        return MachineCommand(*machine_cmd_id_dict['jmple'], arg0=arg0, arg1=arg1, arg2=index)

    @staticmethod
    def jmp_if_greater_or_eq_than(arg0, arg1, index):
        return MachineCommand(*machine_cmd_id_dict['jmpge'], arg0=arg0, arg1=arg1, arg2=index)
