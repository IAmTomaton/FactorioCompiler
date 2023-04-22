import argparse
import base64
import json
import zlib

from MachineCommand import MachineCommand


def combinators_to_blueprint(combinators):
    return {
        'blueprint': {
            'icons': [{'signal': {'type': 'item', 'name': 'constant-combinator'}, 'index': 1}],
            'entities': combinators,
            'item': 'blueprint',
            'version': 281479275544576
        }
    }


def blueprint_to_string(blueprint):
    blueprint_json = json.dumps(blueprint)
    blueprint_zlib = zlib.compress(blueprint_json.encode('utf-8'))
    blueprint_base64 = base64.b64encode(blueprint_zlib)
    blueprint_str = blueprint_base64
    return '0' + blueprint_str.decode('utf-8')


def machine_commands_to_combinators(commands):
    combinators = []
    for i, command in enumerate(commands):
        combinator = command.to_combinator(i, (0, -i))
        combinators.append(combinator)
    return combinators


def machine_commands_to_dense_combinators(commands):
    combinators = []
    max_count = MachineCommand.max_commands_in_combinator
    for i in range(len(commands) // max_count + 1):
        commands_chunk = commands[i * max_count: (i + 1) * max_count]
        combinator = MachineCommand.to_dense_combinator(commands_chunk, i, (0, -i))
        combinators.append(combinator)
    return combinators


def compile_program(input_file, blueprint_file, machine_commands_file):
    from Compiler import Compiler
    compiler = Compiler()

    with open(input_file, 'r') as program:
        lines = list(map(lambda line: line.replace('\n', ''), program))
    commands = compiler.compile_program(lines)

    print(f'{len(commands)} ROM cells used')
    print(f'{len(compiler.variables)} RAM cells required')
    print(f'{len(compiler.temp_variables)} Temp variables count')

    if machine_commands_file:
        with open(machine_commands_file, 'w') as file:
            file.write('\n'.join(map(str, commands)))

    combinators = machine_commands_to_dense_combinators(commands)
    blueprint = combinators_to_blueprint(combinators)
    blueprint_string = blueprint_to_string(blueprint)

    with open(blueprint_file, 'w') as file:
        file.write(blueprint_string)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--source_file', type=str, default='program.txt')
    parser.add_argument('-b', '--blueprint_file', type=str, default='blueprint.txt')
    parser.add_argument('-m', '--machine_cmd_file', type=str, required=False, default=None)
    return parser.parse_args()


def main():
    args = parse_args()
    compile_program(args.source_file, args.blueprint_file, args.machine_cmd_file)


if __name__ == '__main__':
    main()
