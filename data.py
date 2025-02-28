from config import register_data, connection_data


class DataSensors:
    def __init__(self, name: str):
        self.sensors_iterator = -1
        self.send_all = False
        self.dict_sensors = {}        # line no. -> (multi)list [reg_num, fun_code, topic, R/W, dict_attributes]
        self.dict_store_data = {}     # topic -> {value, unit}
        self.dict_writers = {}        # topic -> reg_num
        self.dict_readers = {}        # topic -> line_number in dict_sensors
        self.list_instant_reads = []  # line_number in dict_sensors for instant reading
        self.list_write_regs = []     # reg_num, value(s) to send via ModBUS
        self.topic = connection_data[name]["mqtt_topic_prefix"]
        # prepare dict data
        self.sensor_key = 0
        self.prepareReadSeriesData(register_data[name])
        self.prepareStoreData(register_data[name])
        self.prepareWriteData(register_data[name])
        self.prepareReadData(self.dict_sensors)

    def firstLine(self):
        """Set sensor line at the beginning"""
        self.sensors_iterator = -1
        self.send_all = True        # set send_all flag
        return self.sensors_iterator

    def nextLine(self):
        """Increments sensor line index and returns it"""
        if self.sensors_iterator == len(self.dict_sensors)-1:
            self.send_all = False   # reset send_all flag
        self.sensors_iterator = (self.sensors_iterator + 1) % len(self.dict_sensors)
        return self.sensors_iterator

    def prepareReadSeriesData(self, raw_data):
        """ Method prepares raw sensors data:
            dictionary: line number -> sensor register data """

        def sort(fun_code) -> list:
            # take all lines readable and with specified fun_code
            sorted_sensors_data = [x for x in raw_data if x[1] == fun_code and 'R' in x[3]]
            sorted_sensors_data.sort(key=lambda x: x[0])
            return sorted_sensors_data

        def group(sorted_data):
            if len(sorted_data) > 0:
                temp_list = []
                for sensor in sorted_data:
                    if len(temp_list) == 0 or (sensor[0] - 1) == temp_list[-1][0]:
                        temp_list.append(sensor)
                    else:
                        if len(temp_list) == 1:
                            self.dict_sensors[self.sensor_key] = temp_list[0]
                        else:
                            self.dict_sensors[self.sensor_key] = temp_list
                        self.sensor_key += 1
                        temp_list = [sensor]
                if len(temp_list) == 1:
                    self.dict_sensors[self.sensor_key] = temp_list[0]
                else:
                    self.dict_sensors[self.sensor_key] = temp_list
                self.sensor_key += 1

        # Sort & group sensors input data
        group(sort(4))
        group(sort(3))

    def prepareStoreData(self, raw_data):
        """Methods prepares dict structure to store sensors data: topic -> {value, unit}"""
        for data in raw_data:
            if 'R' in data[3]:
                self.dict_store_data[data[2]] = {
                    "value": None,
                    "unit": data[4].get("unit", "") if len(data) > 4 else ""
                }

    def prepareReadData(self, dict_sensors_data):
        """Prepares dictionary with readable registers: topic -> line number in dict_sensors"""
        for (line_num, list_data) in dict_sensors_data.items():
            if type(list_data[0]) is list:
                for temp_list in list_data:
                    self.dict_readers[temp_list[2]] = line_num
            else:
                self.dict_readers[list_data[2]] = line_num

    def prepareWriteData(self, raw_data):
        """Methods prepares writing sensors dict: topic -> register_num"""
        for data in raw_data:
            # if register is writable and has fun_code = 3
            if 'W' in data[3] and data[1] == 3:
                self.dict_writers[data[2]] = data[0]

    def saveData(self, dict_to_save: dict):
        """ Save changed values in dict_store_data and returns dictionary with changed values: topic -> value """
        new_values = {}
        for (topic, value) in dict_to_save.items():
            # check if value has changed
            if value != self.dict_store_data[topic]["value"] or self.send_all:
                # save value if changed
                self.dict_store_data[topic]["value"] = value
                # save value for MQTT sending
                new_values[topic] = value
        return new_values


# For testing only
def printDict(dict_to_print):
    for (key, value) in dict_to_print.items():
        print(F"{key} -> {value}")


# obj = DataSensors("Rekuperator")
# printDict(obj.dict_sensors)
# printDict(obj.dict_readers)
