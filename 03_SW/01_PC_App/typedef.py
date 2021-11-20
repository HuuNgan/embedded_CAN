from enum import Enum


class deviceStatus(Enum):
    NA = -1
    disconnect = 0
    connect = 1


class modifyTable(Enum):
    add_modify = 0
    delete = 1
    add = 2
    modify = 3


class typePeripheral(Enum):
    NA = -1
    neopixel = 0
    led = 1
    button = 2


class pixelMode(Enum):
    NA = -1
    rainbow = 0
    random = 1
    single = 2
    stop = 3


class buttonStatus(Enum):
    NA = -1
    off = 0
    on = 1


class ledMode(Enum):
    NA = -1
    off = 0
    on = 1


class tableColumn(Enum):
    NA = -1
    ID = 0
    can_id = 1
    device_status = 2
    button_status = 3
    mode_neopixel = 4
    led_status = 5
