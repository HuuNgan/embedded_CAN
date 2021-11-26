from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import (
    QAbstractButton,
    QAbstractItemView,
    QHeaderView,
    QMessageBox,
    QSlider,
    QFrame,
    QTableWidgetItem,
)

import serial
import sys

from typing import *

from main_window import *

from compress_data import *
from typedef import *


class builtTable(Ui_MainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.device_count = 0
        self.row_init = 18

    def init_device_table(self) -> None:
        self.device_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.device_table.setSelectionMode(QAbstractItemView.NoSelection)
        # Set default columnn width
        self.device_table.setColumnWidth(0, 5)
        self.device_table.setColumnWidth(1, 80)
        self.device_table.setColumnWidth(2, 80)
        self.device_table.setColumnWidth(3, 50)
        self.device_table.setColumnWidth(4, 80)
        self.device_table.setColumnWidth(5, 60)
        self.device_table.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)

        # Add row
        self.device_table.verticalHeader().setSectionsClickable(False)
        self.device_table.verticalHeader().setDefaultSectionSize(15)
        self.device_table.verticalHeader().setVisible(False)
        for x in range(self.row_init):
            self.device_table.insertRow(x)

    def add_row_device_table(self) -> None:
        row_count = self.device_table.rowCount()
        self.device_table.insertRow(row_count)

    def delete_row_device_table(self, row_no) -> None:
        self.device_table.removeColumn(row_no)

    def add_item_device_table(
        self,
        can_id: int,
        device_status: deviceStatus,
        button_status: buttonStatus,
        mode_neopixel: pixelMode,
        led_status: ledMode,
    ) -> None:
        if self.device_count > self.device_table.rowCount():
            self.add_row_device_table()

        item = QTableWidgetItem()
        item.setText(str(self.device_count + 1))
        self.device_table.setItem(self.device_count, tableColumn.ID.value, item)

        item = QTableWidgetItem()
        item.setText(str(can_id))
        self.device_table.setItem(self.device_count, tableColumn.can_id.value, item)

        item = QTableWidgetItem()
        item.setText(str(device_status.name.upper()))
        self.device_table.setItem(
            self.device_count, tableColumn.device_status.value, item
        )

        item = QTableWidgetItem()
        item.setText(str(button_status.name.upper()))
        self.device_table.setItem(
            self.device_count, tableColumn.button_status.value, item
        )

        item = QTableWidgetItem()
        item.setText(str(mode_neopixel.name.upper()))
        self.device_table.setItem(
            self.device_count, tableColumn.mode_neopixel.value, item
        )

        item = QTableWidgetItem()
        item.setText(str(led_status.name.upper()))
        self.device_table.setItem(self.device_count, tableColumn.led_status.value, item)

        self.device_count += 1

    def delete_item_device_table(self, row: int) -> None:
        self.device_count -= 1
        self.device_table.removeRow(row)
        row_count = self.device_table.rowCount()
        if row_count < self.row_init:
            self.add_row_device_table()
        for x in range(self.device_count):
            self.device_table.item(x, 0).setText(str(x + 1))

    def change_item_device_table(
        self, row: int, change_column: int, new_value: Any
    ) -> None:
        self.device_table.item(row, change_column).setText(str(new_value))


class GUI(builtTable, CompressData):
    def __init__(self, MainWindow) -> None:
        super(GUI, self).__init__()
        self.setupUi(MainWindow)
        self.init_variable()
        self.init_default_config_window()
        self.init_callback()
        self.init_timer()
        self.init_device_table()
        self.refresh_status_bar()

    def init_variable(self) -> None:
        self.com_connect_status = False
        self.mode: pixelMode = pixelMode.single

        # Status of device
        self.status_CAN_connect = False

        # Timer call for loop process
        self.loop_UART = 100
        self.loop_STATUS_BAR = 5000
        self.loop_DEVICE_STATUS = 2000

        # Max range
        self.max_range_color = 255

        self.ready_to_read = True
        self.combo_box_device_select = []

    def init_timer(self) -> None:
        """
        Add timer for some object
        """

        # Callback get data after 100ms
        self.TIM_UART = QtCore.QTimer()
        self.TIM_UART.setInterval(self.loop_UART)
        self.TIM_UART.timeout.connect(self.get_data)
        self.TIM_UART.start()

        self.TIM_STATUS_BAR = QtCore.QTimer()
        self.TIM_STATUS_BAR.setInterval(self.loop_STATUS_BAR)
        self.TIM_STATUS_BAR.timeout.connect(self.refresh_status_bar)

        self.STATUS_DEVICE = QtCore.QTimer()
        self.STATUS_DEVICE.setInterval(self.loop_DEVICE_STATUS)
        self.STATUS_DEVICE.timeout.connect(self.device_select_callback)

    def init_default_config_window(self) -> None:
        """
        Set default setting when start app
        """

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

        # Generate 100 com in com_select
        for x in range(100):
            com_name = "COM" + str(x + 1)
            self.com_select.addItem(com_name)

        # Set color sample
        self.sample_frame.setFrameStyle(QFrame.Panel | QFrame.Plain)
        self.color_sample()

    def init_callback(self) -> None:
        """
        Add callback for object
        """

        # Callback connect button
        self.connect_button.clicked.connect(self.connect_button_callback)

        # Callback send button
        self.send_button.clicked.connect(self.send_button_callback)

        # Callback radiobox mode
        self.random_select.toggled.connect(
            lambda: self.color_mode_radiobtn_callback(pixelMode.random)
        )
        self.rainbow_select.toggled.connect(
            lambda: self.color_mode_radiobtn_callback(pixelMode.rainbow)
        )
        self.single_select.toggled.connect(
            lambda: self.color_mode_radiobtn_callback(pixelMode.single)
        )

        # Callback when value change in color qlinetext'
        self.blue_value.textChanged.connect(
            lambda: self.color_linetext_change_callback(
                self.blue_value, self.blue_slider
            )
        )
        self.red_value.textChanged.connect(
            lambda: self.color_linetext_change_callback(self.red_value, self.red_slider)
        )
        self.green_value.textChanged.connect(
            lambda: self.color_linetext_change_callback(
                self.green_value, self.green_slider
            )
        )

        # Callback when value change in color slider
        self.blue_slider.valueChanged.connect(
            lambda: self.color_slider_change_callback(self.blue_slider, self.blue_value)
        )
        self.red_slider.valueChanged.connect(
            lambda: self.color_slider_change_callback(self.red_slider, self.red_value)
        )
        self.green_slider.valueChanged.connect(
            lambda: self.color_slider_change_callback(
                self.green_slider, self.green_value
            )
        )

        # Callback when device_select change
        self.device_select.currentTextChanged.connect(self.device_select_callback)

    def color_slider_change_callback(
        self, slider: QSlider, linetext: QtWidgets.QLineEdit
    ) -> None:
        """
        Callback for color slider
        """

        linetext.setText(str(slider.value()))
        self.color_sample()

    def color_linetext_change_callback(
        self, linetext: QtWidgets.QLineEdit, slider: QSlider
    ) -> None:
        """
        Callback for color text edit
        """

        if linetext.text() == "":
            linetext.setText("0")
        if int(linetext.text()) > self.max_range_color:
            linetext.setText(str(self.max_range_color))
        if linetext.text()[0] == "0":
            linetext.setText(str(int(linetext.text())))
        slider.setValue(int(linetext.text()))

        self.color_sample()

    def color_sample(self) -> None:
        """
        Set color background in color sample object
        """

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

    def device_select_callback(self) -> None:
        """
        Callback for status device
        """

        if self.STATUS_DEVICE.isActive() == True:
            self.STATUS_DEVICE.stop()

        self.status_device.setText("Standby")

    def connect_button_callback(self) -> None:
        """
        Callback for color text edit
        """

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

    def color_panel_set_status(self, status: bool) -> None:
        self.green_value.setEnabled(status)
        self.red_value.setEnabled(status)
        self.blue_value.setEnabled(status)
        self.green_slider.setEnabled(status)
        self.red_slider.setEnabled(status)
        self.blue_slider.setEnabled(status)

    def color_mode_radiobtn_callback(self, input: pixelMode) -> None:
        """
        Callback for color mode when change radio button
        """

        if input == pixelMode.random:
            self.color_panel_set_status(False)
        elif input == pixelMode.single:
            self.color_panel_set_status(True)
        elif input == pixelMode.rainbow:
            self.color_panel_set_status(False)

        self.mode = input

    def refresh_status_bar(self):
        if self.TIM_STATUS_BAR.isActive() == True:
            self.TIM_STATUS_BAR.stop()

        can_status = ""

        if str(self.status_CAN_connect) == "True":
            can_status = "CONNECTED"
        else:
            can_status = "DISCONNECTED"

        status_bar = "CAN: " + can_status
        self.statusBar.showMessage(status_bar)

    def modify_table(self, data_block: Dict[str, Any]) -> None:
        row = 0
        action = data_block["action"]
        can_id = data_block["can_id"]
        matching = self.device_table.findItems(str(can_id), QtCore.Qt.MatchExactly)

        if matching == []:
            if action == modifyTable.add_modify:
                action = modifyTable.add
            elif action == modifyTable.delete:
                self.error_msg("Device not register")
                return
        else:
            matching_column = False
            for x in matching:
                if x.column() == 1:
                    if action == modifyTable.add_modify:
                        action = modifyTable.modify
                    row = x.row()
                    matching_column = True
            if not matching_column:
                if action == modifyTable.delete:
                    return
                action = modifyTable.add

        if action == modifyTable.add:
            self.add_item_device_table(
                can_id=data_block["can_id"],
                device_status=data_block["device_status"],
                button_status=data_block["button_status"],
                mode_neopixel=data_block["mode_neopixel"],
                led_status=data_block["led_status"],
            )
            self.combo_box_device_select.append(can_id)
            self.combo_box_device_select.sort()
            self.device_select.clear()
            for x in self.combo_box_device_select:
                self.device_select.addItem(str(x))
        elif action == modifyTable.modify:
            change_column = data_block["change_column"]
            self.change_item_device_table(
                row=row,
                change_column=change_column,
                new_value=str(
                    data_block[str(tableColumn(change_column).name)].name
                ).upper(),
            )
        elif action == modifyTable.delete:
            self.combo_box_device_select.remove(can_id)
            self.combo_box_device_select.sort()
            self.device_select.clear()
            for x in self.combo_box_device_select:
                self.device_select.addItem(str(x))
            self.delete_item_device_table(row=row)

        matching = self.device_table.findItems("1", QtCore.Qt.MatchExactly)
        if matching:
            self.status_CAN_connect = True
        else:
            self.status_CAN_connect = False
        self.refresh_status_bar()

    def get_data(self) -> None:
        """
        Get data in specify time
        """

        bytetoread = []
        if self.com_connect_status == True and self.ready_to_read == True:
            try:
                bytetoread = self.transmit.inWaiting()
                if bytetoread > 0:
                    raw_data = self.transmit.read(bytetoread)
                    self.ready_to_read == False
                    if (
                        raw_data[0] == CompressData().start_flag
                        and raw_data[len(raw_data) - 1] == CompressData().end_flag
                    ):
                        length = raw_data[1]
                        if length == (len(raw_data) - 3):
                            self.modify_table(CompressData.extract_data(raw_data))
                    self.ready_to_read == True
            except IOError:
                self.disconnect_com()
                self.error_msg("COM disconnect unexpected")

    def send_button_callback(self):
        """
        Callback when send button push
        """
        try:
            id_device = int(self.device_select.currentText())
        except:
            id_device = 0x00

        data: bytearray = bytearray()
        if self.mode == pixelMode.rainbow or self.mode == pixelMode.random:
            data = CompressData.compress_data(
                mode=self.mode,
                type_peripheral=typePeripheral.neopixel,
                can_id=id_device,
            )
        elif self.mode == pixelMode.single:
            data = CompressData.compress_data(
                mode=self.mode,
                type_peripheral=typePeripheral.neopixel,
                can_id=id_device,
                red_value=self.red_slider.value(),
                blue_value=self.blue_slider.value(),
                green_value=self.green_slider.value(),
            )

        if self.com_connect_status == True:
            self.transmit.write(data)
            self.status_device.setText("Sent")
            self.STATUS_DEVICE.start()
        else:
            status_bar = "COM is not connected"
            self.statusBar.showMessage(status_bar, msecs=self.loop_STATUS_BAR)
            self.TIM_STATUS_BAR.start()

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
