import minimalmodbus
from config import connection_data


def printDict(dict_to_print):
    [print(F"{k} -> {v}") for (k, v) in dict_to_print.items()]


class ModbusCommunication:
    def __init__(self, name: str):
        self.name = name
        self.settings = connection_data[name]
        self.__init_instrument()

    def __init_instrument(self):
        self.instrument = minimalmodbus.Instrument(self.settings["port"], self.settings["address"])
        self.instrument.mode = self.settings["mode"]
        self.instrument.serial.baudrate = self.settings["baudrate"]
        self.instrument.serial.bytesize = self.settings["bytesize"]
        self.instrument.serial.parity = self.settings["parity"]
        self.instrument.serial.stopbits = self.settings["stopbits"]
        self.instrument.serial.timeout = 1  # reading timeout 1 second
        # self.instrument.debug = True

    def read_data(self, dict_read_data: dict, index: int):
        """Reads register(s) from dictionary under specific index key and returns results in
        small dictionary topic -> value"""
        if type(dict_read_data[index][0]) is list:
            dict_result = self.read_several_registers(dict_read_data[index])
        else:
            dict_result = self.read_one_register(dict_read_data[index])
        # printDict(dict_result)
        return dict_result

    def read_one_register(self, sensor_line: list):
        """Reads one register from list and return results in dictionary: topic -> value.
        List input format: [reg_num, fun_code, topic]"""
        ret_dict = {}
        reg_num = sensor_line[0]
        fun_code = sensor_line[1]
        topic = sensor_line[2]
        dec = sensor_line[4].get("dec", 0) if len(sensor_line) > 4 else 0
        is_signed = bool(sensor_line[4].get("signed", "False")) if len(sensor_line) > 4 else False
        # Read register
        value = self.instrument.read_register(reg_num, dec, functioncode=fun_code, signed=is_signed)
        # Add result to dict
        ret_dict[topic] = value
        return ret_dict

    def read_several_registers(self, sensors_list: list):
        """Reads several registers and returns results in dictionary
        List input format: [reg_num, fun_code, topic]"""
        ret_dict = {}
        reg_count = len(sensors_list)
        sensor_line = sensors_list[0]
        reg_num = sensor_line[0]
        fun_code = sensor_line[1]
        values_list = self.instrument.read_registers(reg_num, reg_count, functioncode=fun_code)
        # print(values_list)
        for i in range(len(values_list)):
            topic = sensors_list[i][2]
            dec = sensors_list[i][4].get("dec", 0) if len(sensors_list[i]) > 4 else 0
            value = (values_list[i] / (10 * dec)) if dec > 0 else values_list[i]
            # Add result to dict
            ret_dict[topic] = value
        return ret_dict

    def write_data(self, reg_addr, data):
        if type(data) is list:
            self.write_several_registers(reg_addr, data)
        else:
            self.write_one_register(reg_addr, data)

    def write_one_register(self, reg_addr, value):
        self.instrument.write_register(reg_addr, value)

    def write_several_registers(self, reg_addr, values: list):
        self.instrument.write_registers(reg_addr, values)
