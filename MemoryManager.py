from MachineCommand import MachineCommand


class MemoryManager:

    def __init__(self, register_count):
        self.register_count = register_count
        self.temp_variables_reg_offset = 3
        self.temp_variables_reg_count = self.register_count - self.temp_variables_reg_offset

        self.next_var_index = self.register_count

        self.variables = {}
        self.temp_variables = []

        self.temp_var_prefix = '__temp_var'

        for i in range(self.temp_variables_reg_count):
            temp_var = self.get_temp_var_by_index(i)
            self.variables[temp_var] = i + self.temp_variables_reg_offset
            self.temp_variables.append(temp_var)

        self.ALU_output_var = '__ALU_output'
        self.variables[self.ALU_output_var] = 0

    def get_temp_var_by_index(self, index):
        return self.temp_var_prefix + str(index)

    def try_add_variable(self, var):
        if var not in self.variables:
            self.variables[var] = self.next_var_index
            self.next_var_index += 1
            return self.variables[var], True
        return self.variables[var], False

    def get_or_create_temp_var(self, index):
        temp_var = self.get_temp_var_by_index(index)
        address, result = self.try_add_variable(temp_var)
        if result:
            self.temp_variables.append(temp_var)
        return temp_var, result

    def load_to_reg(self, arg, reg):
        if reg <= 0 or reg >= self.register_count:
            raise Exception(f'Reg out of rage {reg}')

        if arg is int or arg.isdigit():
            return reg, MachineCommand.put(arg, reg)

        address = self.variables[arg]
        if address < self.register_count:
            return address, None
        return reg, MachineCommand.move(address, reg)

    def move_or_put(self, arg, address):
        if arg is int or arg.isdigit():
            return MachineCommand.put(arg, address)
        else:
            return MachineCommand.move(self.variables[arg], address)
