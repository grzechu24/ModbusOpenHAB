import time
from data import DataSensors
from modbus import ModbusCommunication


class ModbusDevice:

    def __init__(self, name: str):
        self.offline_timer = 0
        # Objects
        self.sensors_data = DataSensors(name)
        self.modbus_conn = ModbusCommunication(name)

    def addAdditionalRegisters(self, dict_data):
        """Adds additional virtual registers for sending"""
        dict_data["online"] = 1
        return dict_data

    def addReadBackRegister(self, register_name: str):
        """Adds line numbers of registers in dict_sensors for instant reading
        It prevents adding duplicates"""
        line_num = self.sensors_data.dict_readers.get(register_name, -1)
        if line_num >= 0 and line_num not in self.sensors_data.list_instant_reads:
            self.sensors_data.list_instant_reads.append(line_num)

    def addWriteRegister(self, topic: str, values):
        """Adds register number and values to send to the list"""
        reg_addr = self.sensors_data.dict_writers.get(topic, -1)
        if reg_addr >= 0 and values is not None:
            self.sensors_data.list_write_regs.append([reg_addr, values])

    def isEnable(self):
        """Returns true when offline delay has gone"""
        return time.time() > self.offline_timer

    def getMqttTopic(self):
        return self.sensors_data.topic

    def printDataTable(self):
        for (key, dict_value) in self.sensors_data.dict_store_data.items():
            print(f"{key} = {dict_value['value']} {dict_value.get('unit', '')}")

    def readRegisters(self):
        """Reads one series of register from data and returns dictionary (topic -> value), which has been changed
        or send all"""
        dict_sensors = self.sensors_data.dict_sensors
        if len(self.sensors_data.list_instant_reads) > 0:
            index_sensors = self.sensors_data.list_instant_reads.pop(0)
        else:
            index_sensors = self.sensors_data.nextLine()
        dict_results = self.modbus_conn.read_data(dict_sensors, index_sensors)
        dict_results = self.addAdditionalRegisters(dict_results)
        return self.sensors_data.saveData(dict_results)

    def receive(self, topic, value):
        pass

    def setOffline(self):
        """Set delay time when device is offline to prevent pooling it every second
        Returns dict with offline MQTT topic"""
        self.offline_timer = time.time() + 60
        return {"online": 0}

    def updateAllRegisters(self):
        """Method for sending all register values via MQTT every some time"""
        self.sensors_data.firstLine()

    def writeRegisters(self):
        """Writes all registers from dictionary to MODBus device"""
        while len(self.sensors_data.list_write_regs) > 0:
            package = self.sensors_data.list_write_regs.pop(0)
            self.modbus_conn.write_data(package[0], package[1])


class ThesslaDevice(ModbusDevice):

    def receive(self, topic, value):
        match topic:
            case "airFlowRateTemporary":
                self.__changeFlowRateTemporary(int(value))
            case "airFlowRateManual":
                self.__changeFlowRateManual(int(value))
            case "cfgMode1":
                self.__changeModeAuto()
            case "wietrzenie":
                self.__specialMode(topic, int(value))
            case "kominek":
                self.__specialMode(topic, int(value))
            case "windowOpen":
                self.__specialMode(topic, int(value))
            case "emptyHouse":
                self.__specialMode(topic, int(value))
            case _:
                self.addWriteRegister(topic, int(value))

    def addAdditionalRegisters(self, dict_data):
        """Adds additional virtual registers for sending"""
        dict_data = super().addAdditionalRegisters(dict_data)
        mode = dict_data.get("mode", -1)
        if mode >= 0:
            dict_data["modeAuto"] = 1 if (mode == 0) else 0
        special_mode = dict_data.get("specialMode", -1)
        if special_mode >= 0:
            dict_data["kominek"] = 1 if (special_mode == 2) else 0
            dict_data["wietrzenie"] = 1 if (special_mode == 7) else 0
            dict_data["windowOpen"] = 1 if (special_mode == 10) else 0
            dict_data["emptyHouse"] = 1 if (special_mode == 11) else 0
        return dict_data

    def __changeFlowRateTemporary(self, flow_rate: int):
        """Changes flow rate as temporary value in % """
        if 0 <= int(flow_rate) <= 100:
            # Write "cfgMode1"
            self.addWriteRegister("cfgMode1", [2, int(flow_rate), 1])
            # Read back
            self.addReadBackRegister("mode")
            self.addReadBackRegister("supply_percentage")
            self.addReadBackRegister("supplyAirFlow")
            self.addReadBackRegister("exhaustAirFlow")

    def __changeFlowRateManual(self, flow_rate: int):
        """Changes flow rate in manual mode in % """
        if 0 <= int(flow_rate) <= 100:
            # Write "airFlowRateManual"
            self.addWriteRegister("airFlowRateManual", int(flow_rate))
            # Read back
            self.addReadBackRegister("mode")
            self.addReadBackRegister("supply_percentage")
            self.addReadBackRegister("supplyAirFlow")
            self.addReadBackRegister("exhaustAirFlow")

    def __changeModeAuto(self):
        """Change mode to automatic"""
        # Write "cfgMode1"
        self.addWriteRegister("cfgMode1", 0)
        # Read back
        self.addReadBackRegister("mode")
        self.addReadBackRegister("supply_percentage")
        self.addReadBackRegister("supplyAirFlow")
        self.addReadBackRegister("exhaustAirFlow")

    def __specialMode(self, name: str, value: int):
        # Write "specialMode"
        match name:
            case "wietrzenie":
                self.addWriteRegister("specialMode", 7 if (value == 1) else 0)
            case "kominek":
                self.addWriteRegister("specialMode", 2 if (value == 1) else 0)
            case "windowOpen":
                self.addWriteRegister("specialMode", 10 if (value == 1) else 0)
            case "emptyHouse":
                self.addWriteRegister("specialMode", 11 if (value == 1) else 0)
        # Read back
        self.addReadBackRegister("supply_percentage")
