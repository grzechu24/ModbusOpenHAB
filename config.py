import minimalmodbus

register_data = {
    "Rekuperator": [
        [-1,-1, "online", 'R'],  # device online
        [16, 4, "outside_temp", 'R', {"dec": 1, "unit": '°C', "signed": True}],  # wyrzutnia
        [17, 4, "supply_temp", 'R', {"dec": 1, "unit": '°C', "signed": True}],  # nawiew
        [18, 4, "exhaust_temp", 'R', {"dec": 1, "unit": '°C', "signed": True}],  # wywiew
        [19, 4, "fpx_temp", 'R', {"dec": 1, "unit": '°C', "signed": True}],  # czerpnia
        [22, 4, "ambient_temp", 'R', {"dec": 1, "unit": '°C', "signed": True}],  # otoczenie
        [272, 4, "supply_percentage", 'R', {"unit": '%'}],  # zadany nawiew [%]
        [273, 4, "exhaust_percentage", 'R', {"unit": '%'}],  # zadany wywiew [%]
        [274, 4, "supply_flowrate", 'R', {"unit": 'm3/h'}],  # zadany nawiew [m3/h]
        [275, 4, "exhaust_flowrate", 'R', {"unit": 'm3/h'}],  # zadany wywiew [m3/h]
        [256, 3, "supplyAirFlow", 'R', {"unit": 'm3/h'}],  # bieżący nawiew [m3/h]
        [257, 3, "exhaustAirFlow", 'R', {"unit": 'm3/h'}],  # bieżący wywiew [m3/h]
        [4198, 3, "antifreezStage", 'R'],  # bieżący tryb systemu FPX: 0-off, 1-FPX1, 2-FPX2
        [4208, 3, "mode", 'R'],  # tryb pracy: auto, manu, chwila
        [-1,  -1, "modeAuto", 'R'],  # tryb pracy auto (virtual)
        [4209, 3, "seasonMode", 'R/W'],  # wybór harmonogramu w trybie AUTO: 0-lato, 1-zima
        [4210, 3, "airFlowRateManual", 'R/W', {"unit": '%'}],  # intensywność w trybie MANUALNYM [%]
        [4400, 3, "cfgMode1", 'W'],  # tryb pracy: auto / manu / chwila
        [4401, 3, "airFlowRateTemporary", 'W', {"unit": '%'}],  # zadana intensywność chwilowa w [%]
        [4402, 3, "airflowRateChangeFlag", 'W'],  # wymuszenie trybu chwilowego
        [4330, 3, "bypassMode", 'R'],  # bypass: 0-nieaktywny, 1-grzanie, 2-chłodzenie
        [4704, 3, "postHeaterERVon", 'R'],  # nagrzewnica ERV: 0-off, 1-on
        [4224, 3, "specialMode", 'R/W'],  # funkcje specjalne
        [-1,  -1, "kominek", 'R/W'],  # funkcja kominek #2 (sama się wyłącza)
        [-1,  -1, "wietrzenie", 'R/W'],  # funkcja wietrzenia #7 (sama się wyłącza)
        [-1,  -1, "windowOpen", 'R/W'],  # funkcja otwarte okno #10
        [-1,  -1, "emptyHouse", 'R/W'],  # funkcja pusty dom #11
    ],
    "Falownik": [
        [-1, -1, "online", 'R'],  # device online
        [0x0000, 3, "operating_state", 'R'],    # operating state: 0-wait, 1-check, 2-normal, 3-fault, 4-permanent
        [0x0006, 3, "PV1volt", 'R', {"dec": 1, "unit": 'V'}],  # input voltage
        [0x0007, 3, "PV1curr", 'R', {"dec": 10, "unit": 'A'}],   # input current
        [0x0008, 3, "PV2volt", 'R', {"dec": 1, "unit": 'V'}],
        [0x0009, 3, "PV2curr", 'R', {"dec": 10, "unit": 'A'}],
        [0x000C, 3, "output_power", 'R', {"dec": 10, "unit": 'kW'}],
        [0x000F, 3, "A-phaseVolt", 'R', {"dec": 1, "unit": 'V'}],   # output voltage phase A
        [0x0010, 3, "A-phaseCurr", 'R', {"dec": 10, "unit": 'A'}],  # output current phase A
        [0x0011, 3, "B-phaseVolt", 'R', {"dec": 1, "unit": 'V'}],
        [0x0012, 3, "B-phaseCurr", 'R', {"dec": 10, "unit": 'A'}],
        [0x0013, 3, "C-phaseVolt", 'R', {"dec": 1, "unit": 'V'}],
        [0x0014, 3, "C-phaseCurr", 'R', {"dec": 10, "unit": 'A'}],
        [0x0019, 3, "today_production", 'R', {"dec": 10, "unit": 'kWh'}],
        [0x001A, 3, "today_prod_time", 'R', {"unit": "min"}],
    ]
}

connection_data = {
    "Rekuperator": {
        "port": "/dev/serial0",
        "mode": minimalmodbus.MODE_RTU,
        "address": 10,
        "baudrate": 9600,
        "bytesize": 8,
        "parity": minimalmodbus.serial.PARITY_NONE,
        "stopbits": 1,
        "mqtt_topic_prefix": 'REKU',
    },
    "Falownik": {
        "port": "/dev/serial0",
        "mode": minimalmodbus.MODE_RTU,
        "address": 1,
        "baudrate": 9600,
        "bytesize": 8,
        "parity": minimalmodbus.serial.PARITY_NONE,
        "stopbits": 1,
        "mqtt_topic_prefix": "FV",
    }
}

# [register, functioncode, MQTT_topic, settings {decimal, unit, signed}]
