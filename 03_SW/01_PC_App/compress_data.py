from operator import mod
from typing import *

from typedef import *


class CompressData:
    def __init__(self) -> None:
        self.start_flag = 0x02
        self.end_flag = 0x0A

    @staticmethod
    def convert_bytearray_to_int():
        pass

    @staticmethod
    def compress_data(
        mode: pixelMode,
        type_peripheral: typePeripheral,
        can_id: int,
        red_value: int = None,
        green_value: int = None,
        blue_value: int = None,
    ) -> bytearray:
        """
        Transmit data frame:
        -----------------------------------------------------------------------------------
        | START FLAG | LENGTH | CAN ID DEVICE | TYPE PERIPHERAL | MODE | COLOR | END FLAG |
        -----------------------------------------------------------------------------------

        COLOR block:
        - Single color mode:
        ----------------------------------------
        | RED VALUE | GREEN VALUE | BLUE VALUE |
        ----------------------------------------

        - Rainbow/random mode:
            - Do not have color block
        """

        transmit_data: List[int] = [CompressData().start_flag]
        data: List[int] = [can_id, int(type_peripheral.value), int(mode.value)]

        if mode == pixelMode.single:
            data.append(red_value)
            data.append(green_value)
            data.append(blue_value)

        transmit_data.append(len(bytearray(data)))

        for x in range(len(data)):
            transmit_data.append(data[x])

        transmit_data.append(CompressData().end_flag)
        return bytearray(transmit_data)

    @staticmethod
    def extract_data(recieve_data: bytearray) -> Dict[str, Any]:
        """
        Receive data frame:
        ------------------------------------------------------------------------
        |START FLAG | LENGTH | CAN ID DEVICE | STATUS | MODE | DATA | END FLAG |
        ------------------------------------------------------------------------

        DATA block:
        - Add/modify mode:
        --------------------------
        | TYPE PERIPHERAL | MODE |
        --------------------------
            - TYPE PERIPHERAL:
            - MODE:
        - Delete mode:
            - Do not have data block
        """

        return_dict = {}
        can_id = recieve_data[2]
        device_status = deviceStatus(recieve_data[3])
        action = modifyTable(recieve_data[4])
        type_peripheral = typePeripheral.NA

        button_status = buttonStatus.NA
        mode_neopixel = pixelMode.NA
        led_status = ledMode.NA
        change_column = tableColumn.NA.value

        try:
            peripheral = recieve_data[5]
        except:
            peripheral = -1

        try:
            data_value = recieve_data[6]
        except:
            data_value = -1

        if action == modifyTable.add_modify:
            type_peripheral = typePeripheral(peripheral)
            if type_peripheral == typePeripheral.neopixel:
                mode_neopixel = pixelMode(data_value)
                change_column = tableColumn.mode_neopixel.value
            elif type_peripheral == typePeripheral.led:
                led_status = ledMode(data_value)
                change_column = tableColumn.led_status.value
            elif type_peripheral == typePeripheral.button:
                button_status = buttonStatus(data_value)
                change_column = tableColumn.button_status.value

        return_dict.update({"can_id": can_id})
        return_dict.update({"device_status": device_status})
        return_dict.update({"action": action})
        return_dict.update({"type_peripheral": type_peripheral})
        return_dict.update({"button_status": button_status})
        return_dict.update({"mode_neopixel": mode_neopixel})
        return_dict.update({"led_status": led_status})
        return_dict.update({"change_column": change_column})

        return return_dict
