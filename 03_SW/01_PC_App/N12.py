from PyQt5 import QtCore, QtGui, QtWidgets

from enum import Enum

import serial
import sys

from typing import *
from main_window import *


class pixel_led_mode(Enum):
    rainbow = 0
    random = 1
    single = 2
    stop = 3


class GUI(Ui_MainWindow):
    def __init__(self, MainWindow) -> None:
        super(GUI, self).__init__()
        self.setupUi(MainWindow)
        self.init_variable()
        self.init_default_config_window()
        self.init_callback()
        self.init_timer()
        self.refresh_status_bar()

    def init_variable(self) -> None:
        self.com_connect_status = False
        self.mode: pixel_led_mode = pixel_led_mode.single

        # Status of device
        self.status_CAN_connect = False
        self.status_button_push = False

        # Timer call for loop process
        self.loop_UART = 100
        self.loop_STATUS_BAR = 5000

    def init_timer(self) -> None:
        # Callback get data after 100ms
        self.TIM_UART = QtCore.QTimer()
        self.TIM_UART.setInterval(self.loop_UART)
        self.TIM_UART.timeout.connect(self.getdata)
        self.TIM_UART.start()

        self.TIM_STATUS_BAR = QtCore.QTimer()
        self.TIM_STATUS_BAR.setInterval(self.loop_STATUS_BAR)
        self.TIM_STATUS_BAR.timeout.connect(self.refresh_status_bar)

    def init_default_config_window(self) -> None:
        # Connect button
        self.connect_button.setText("CONNECT")
        self.connect_button.setStyleSheet("QPushButton {color: green;}")

        # Radio button
        self.single_select.setChecked(True)

        # Default value and type input text editor
        validator = QtGui.QIntValidator(0, 255, self.groupBox_4)

        self.blue_value.setText("0")
        self.blue_value.setValidator(validator)
        self.red_value.setText("0")
        self.red_value.setValidator(validator)
        self.green_value.setText("0")
        self.green_value.setValidator(validator)

    def init_callback(self) -> None:
        # Callback connect button
        self.connect_button.clicked.connect(self.connectbtn)

        # Callback send button
        self.send_button.clicked.connect(self.sendbtn)

        # Callback radiobox mode
        self.random_select.toggled.connect(
            lambda: self.get_mode_radio_button(pixel_led_mode.random)
        )
        self.rainbow_select.toggled.connect(
            lambda: self.get_mode_radio_button(pixel_led_mode.rainbow)
        )
        self.single_select.toggled.connect(
            lambda: self.get_mode_radio_button(pixel_led_mode.single)
        )

        # Callback when value change in qlinetext'
        self.blue_value.textChanged.connect(
            lambda: self.limit_number_input(self.blue_value)
        )
        self.red_value.textChanged.connect(
            lambda: self.limit_number_input(self.red_value)
        )
        self.green_value.textChanged.connect(
            lambda: self.limit_number_input(self.green_value)
        )

    def limit_number_input(self, qlineedit_name: QtWidgets.QLineEdit):
        if int(qlineedit_name.text()) > 255:
            qlineedit_name.setText("255")
        if qlineedit_name.text()[0] == "0":
            qlineedit_name.setText(str(int(qlineedit_name.text())))

    def connectbtn(self) -> None:
        NameCOM = self.com_select.currentText()
        try:
            if self.com_connect_status == False:
                # for windows
                self.transmit = serial.Serial(NameCOM, 115200, timeout=2.5)
                # for ubuntu
                # self.transmit = serial.Serial("/dev/pts/5",115200,timeout=2.5)
                self.com_select.setEnabled(False)
                self.connect_button.setText("DISCONNECT")
                self.connect_button.setStyleSheet("QPushButton {color: red;}")
                self.com_connect_status = True
                self.com_choice = NameCOM

                status_bar = "Serial port " + NameCOM + " opened"
                self.statusBar.showMessage(status_bar, msecs=self.loop_STATUS_BAR)
                self.TIM_STATUS_BAR.start()
            else:
                self.com_select.setEnabled(True)
                self.transmit.close()
                self.connect_button.setText("CONNECT")
                self.connect_button.setStyleSheet("QPushButton {color: green;}")
                self.com_connect_status = False
                self.com_choice = ""

                status_bar = "Serial port " + NameCOM + " closed"
                self.statusBar.showMessage(status_bar, msecs=self.loop_STATUS_BAR)
                self.TIM_STATUS_BAR.start()
        except IOError:
            status_bar = "Serial port " + NameCOM
            if self.com_connect_status == False:
                status_bar += " opening "
            else:
                status_bar += " closing "
            self.statusBar.showMessage(status_bar, msecs=self.loop_STATUS_BAR)
            self.TIM_STATUS_BAR.start()

    def get_mode_radio_button(self, input: pixel_led_mode) -> None:
        if input == pixel_led_mode.random:
            self.green_value.setEnabled(False)
            self.red_value.setEnabled(False)
            self.blue_value.setEnabled(False)
        elif input == pixel_led_mode.single:
            self.green_value.setEnabled(True)
            self.red_value.setEnabled(True)
            self.blue_value.setEnabled(True)
        elif input == pixel_led_mode.rainbow:
            self.green_value.setEnabled(False)
            self.red_value.setEnabled(False)
            self.blue_value.setEnabled(False)

        self.mode = input

    def get_color_value(self) -> Tuple[int]:
        return_data: tuple = ()
        return_data += (int(self.red_value.text()),)
        return_data += (int(self.blue_value.text()),)
        return_data += (int(self.green_value.text()),)
        return return_data

    def sendbtn(self):
        data = str(self.mode.name)

        if self.mode == pixel_led_mode.single:
            for x in self.get_color_value():
                data += "_"
                data += str(x)

        if self.com_connect_status == True:
            data += "\r\n"
            self.transmit.write(data.encode())
        else:
            status_bar = "COM is not connected"
            self.statusBar.showMessage(status_bar, msecs=self.loop_STATUS_BAR)
            self.TIM_STATUS_BAR.start()

    def refresh_status_bar(self):
        if self.TIM_STATUS_BAR.isActive() == True:
            self.TIM_STATUS_BAR.stop()

        status_bar = "CAN: " + str(self.status_CAN_connect).upper()
        status_bar += "    "
        status_bar += "BUTTON DEVICE 1: " + str(self.status_button_push).upper()
        self.statusBar.showMessage(status_bar)

    def process_receive_data(self, input: str) -> None:
        cache = int(input)
        self.status_CAN_connect = bool(cache & 0x1)
        self.status_button_push = bool((cache >> 1) & 0x1)
        self.refresh_status_bar()

    def getdata(self) -> None:
        bytetoread = []
        if self.com_connect_status == True:
            bytetoread = self.transmit.inWaiting()
            if bytetoread > 0:
                # maindata=str(self.transmit.read(bytetoread),'utf-8')
                raw_data = str(self.transmit.read(bytetoread))
                raw_data = raw_data.replace("'", "")
                raw_data = raw_data[1:]
                self.process_receive_data(raw_data)


def UIbuild():
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = GUI(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    UIbuild()
