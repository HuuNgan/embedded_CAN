from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox, QSlider, QFrame

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
        self.init_generate_com_select()
        self.init_variable()
        self.init_default_config_window()
        self.init_callback()
        self.init_timer()
        self.init_table()
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

        # Max range
        self.max_range_color = 255

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
        validator = QtGui.QIntValidator(0, 255, self.color_grbox)

        self.blue_value.setText("0")
        self.blue_value.setValidator(validator)
        self.red_value.setText("0")
        self.red_value.setValidator(validator)
        self.green_value.setText("0")
        self.green_value.setValidator(validator)

        # Default max range color
        self.green_slider.setMaximum(self.max_range_color)
        self.red_slider.setMaximum(self.max_range_color)
        self.blue_slider.setMaximum(self.max_range_color)

        # Set color sample
        self.sample_frame.setFrameStyle(QFrame.Panel | QFrame.Plain)
        self.color_sample()

    def init_callback(self) -> None:
        # Callback connect button
        self.connect_button.clicked.connect(self.connectbtn)

        # Callback send button
        self.send_button.clicked.connect(self.send_data)

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

        # Callback when value change in color qlinetext'
        self.blue_value.textChanged.connect(
            lambda: self.color_linetext_change(self.blue_value, self.blue_slider)
        )
        self.red_value.textChanged.connect(
            lambda: self.color_linetext_change(self.red_value, self.red_slider)
        )
        self.green_value.textChanged.connect(
            lambda: self.color_linetext_change(self.green_value, self.green_slider)
        )

        # Callback when value change in color slider
        self.blue_slider.valueChanged.connect(
            lambda: self.color_slider_change(self.blue_slider, self.blue_value)
        )
        self.red_slider.valueChanged.connect(
            lambda: self.color_slider_change(self.red_slider, self.red_value)
        )
        self.green_slider.valueChanged.connect(
            lambda: self.color_slider_change(self.green_slider, self.green_value)
        )

    def init_generate_com_select(self) -> None:
        for x in range(100):
            com_name = "COM" + str(x + 1)
            self.com_select.addItem(com_name)

    def init_table(self) -> None:
        self.device_table.verticalHeader().setDefaultSectionSize(10)

    def color_slider_change(
        self, slider: QSlider, linetext: QtWidgets.QLineEdit
    ) -> None:
        linetext.setText(str(slider.value()))
        self.color_sample()

    def color_linetext_change(
        self, linetext: QtWidgets.QLineEdit, slider: QSlider
    ) -> None:
        if int(linetext.text()) > self.max_range_color:
            linetext.setText(str(self.max_range_color))
        if linetext.text()[0] == "0":
            linetext.setText(str(int(linetext.text())))
        slider.setValue(int(linetext.text()))

        self.color_sample()

    def color_sample(self) -> None:
        color_sample = (
            "background-color:rgb("
            + str(self.red_slider.value())
            + ","
            + str(self.green_slider.value())
            + ","
            + str(self.blue_slider.value())
            + ")"
        )
        self.sample_frame.setStyleSheet(color_sample)

    def connectbtn(self) -> None:
        NameCOM = self.com_select.currentText()
        try:
            if self.com_connect_status == False:
                self.connect_com(NameCOM)
            else:
                self.disconnect_com()
        except IOError:
            status_bar = "Serial port " + NameCOM
            if self.com_connect_status == False:
                status_bar += " error when open port !"
            else:
                status_bar += " error when close port !"
            self.statusBar.showMessage(status_bar, msecs=self.loop_STATUS_BAR)
            self.TIM_STATUS_BAR.start()

    def connect_com(self, com) -> None:
        # for windows
        self.transmit = serial.Serial(com, 115200, timeout=2.5)
        # for ubuntu
        # self.transmit = serial.Serial("/dev/pts/5",115200,timeout=2.5)
        self.com_select.setEnabled(False)
        self.connect_button.setText("DISCONNECT")
        self.connect_button.setStyleSheet("QPushButton {color: red;}")
        self.com_connect_status = True
        self.com_choice = com

        status_bar = "Serial port " + self.com_choice + " opened"
        self.statusBar.showMessage(status_bar, msecs=self.loop_STATUS_BAR)
        self.TIM_STATUS_BAR.start()

    def disconnect_com(self) -> None:
        self.com_select.setEnabled(True)
        self.transmit.close()
        self.connect_button.setText("CONNECT")
        self.connect_button.setStyleSheet("QPushButton {color: green;}")
        self.com_connect_status = False

        status_bar = "Serial port " + self.com_choice + " closed"
        self.com_choice = ""

        self.statusBar.showMessage(status_bar, msecs=self.loop_STATUS_BAR)
        self.TIM_STATUS_BAR.start()

    def disconnect_com_exp(self) -> None:
        self.com_select.setEnabled(True)
        self.connect_button.setText("CONNECT")
        self.connect_button.setStyleSheet("QPushButton {color: green;}")
        self.com_connect_status = False
        self.com_choice = ""

    def color_enable(self, status: bool) -> None:
        self.green_value.setEnabled(status)
        self.red_value.setEnabled(status)
        self.blue_value.setEnabled(status)
        self.green_slider.setEnabled(status)
        self.red_slider.setEnabled(status)
        self.blue_slider.setEnabled(status)

    def get_mode_radio_button(self, input: pixel_led_mode) -> None:
        if input == pixel_led_mode.random:
            self.color_enable(False)
        elif input == pixel_led_mode.single:
            self.color_enable(True)
        elif input == pixel_led_mode.rainbow:
            self.color_enable(False)

        self.mode = input

    def get_color_value(self) -> Tuple[int]:
        return_data: tuple = ()
        return_data += (int(self.red_value.text()),)
        return_data += (int(self.blue_value.text()),)
        return_data += (int(self.green_value.text()),)
        return return_data

    def send_data(self):
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
            try:
                bytetoread = self.transmit.inWaiting()
                if bytetoread > 0:
                    # maindata=str(self.transmit.read(bytetoread),'utf-8')
                    raw_data = str(self.transmit.read(bytetoread))
                    raw_data = raw_data.replace("'", "")
                    raw_data = raw_data[1:]
                    self.process_receive_data(raw_data)
            except:
                self.disconnect_com_exp()
                self.error_msg("COM disconnect unexpected")

    def error_msg(self, text):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText(text)
        msg.setWindowTitle("Error")
        msg.exec_()


def UIbuild():
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = GUI(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    UIbuild()
