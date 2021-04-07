from enum import IntEnum
from typing import Optional, Dict

import cv2
import easygui
from PyQt5 import QtCore, QtGui, QtWidgets, QtNetwork
from PyQt5.QtCore import pyqtSlot

import esp_status
from esp_status import EspMode
import esp_wifi
from contour_iterator import ContourIterator
from gui import Ui_MainWindow

main_window = None  # type: Optional[QtWidgets.QMainWindow]


class RobotGuiState(IntEnum):
    NO_IMAGE = 0
    IMAGE_LOADED = 1
    READY_TO_DRAW = 2
    DRAWING = 3
    PAUSED = 4


class SocketWrapper(QtCore.QObject):
    def __init__(self, parent: "RobotMainWindow", socket: QtNetwork.QTcpSocket):
        super().__init__(parent)
        self.socket = socket
        self.data = bytearray()
        self.parent = parent

        self.socket.readyRead.connect(self.handle_incoming_data)
        self.socket.disconnected.connect(self.handle_socket_disconn)

        if self.socket.bytesAvailable() > 0:
            self.handle_incoming_data()

    @pyqtSlot()
    def handle_incoming_data(self):
        new_data = self.socket.readAll()
        self.data.extend(new_data.data())

        print(f"Read {len(new_data)} from {self.socket.peerAddress().toString()}")

    @pyqtSlot()
    def handle_socket_disconn(self):
        print(f"Connection from {self.socket.peerAddress().toString()} closed")

        esp_wifi.handle_packet(self.data, self.socket.peerAddress().toString(), self.parent.esp_table)

        self.parent.handle_close_connection(self)


class RobotMainWindow(QtWidgets.QMainWindow):
    @pyqtSlot()
    def handle_new_connection(self):
        while self.server.hasPendingConnections():
            client = self.server.nextPendingConnection()
            print(f"New connection from {client.peerAddress().toString()}")

            wrapper = SocketWrapper(self, client)
            self.sockets.append(wrapper)

    def handle_close_connection(self, wrapper: SocketWrapper):
        self.sockets.remove(wrapper)

    @pyqtSlot(int)
    def esp_status_changed(self, dev_id: int):
        pass

    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.image_path = None
        self.contour_segments = None
        self.contour_iter_prime = None  # type: Optional[ContourIterator]
        self.contour_iter_second = None  # type: Optional[ContourIterator]

        self.current_state = RobotGuiState.NO_IMAGE

        self.esp_table = esp_status.DeviceTable(self)
        self.esp_table.device_modified.connect(self.esp_status_changed)
        self.ui.esp_table_view.setModel(self.esp_table)
        self.ui.esp_table_view.show()

        self.sockets = []
        self.server = QtNetwork.QTcpServer(self)
        self.server.newConnection.connect(self.handle_new_connection)
        self.server.listen(QtNetwork.QHostAddress.AnyIPv4, esp_wifi.SERV_PORT)

    def change_state(self, new_state: RobotGuiState):
        if new_state == RobotGuiState.NO_IMAGE:
            self.ui.processButton.setEnabled(False)
            self.ui.drawButton.setEnabled(False)
            self.ui.pause_draw_button.setEnabled(False)
            self.ui.stop_draw_button.setEnabled(False)

        elif new_state == RobotGuiState.IMAGE_LOADED:
            self.ui.processButton.setEnabled(True)
            self.ui.drawButton.setEnabled(False)
            self.ui.pause_draw_button.setEnabled(False)
            self.ui.stop_draw_button.setEnabled(False)

        elif new_state == RobotGuiState.READY_TO_DRAW:
            self.ui.processButton.setEnabled(True)
            self.ui.drawButton.setEnabled(not self.esp_table.is_empty)
            self.ui.pause_draw_button.setEnabled(False)
            self.ui.stop_draw_button.setEnabled(False)

        elif new_state == RobotGuiState.DRAWING:
            self.ui.processButton.setEnabled(False)
            self.ui.drawButton.setEnabled(False)
            self.ui.pause_draw_button.setEnabled(True)
            self.ui.stop_draw_button.setEnabled(True)

        elif new_state == RobotGuiState.PAUSED:
            self.ui.processButton.setEnabled(False)
            self.ui.drawButton.setEnabled(True)
            self.ui.pause_draw_button.setEnabled(True)
            self.ui.stop_draw_button.setEnabled(True)

    @pyqtSlot()
    def on_cTestButton_clicked(self):
        print("Connection Test")
        # TODO

    @pyqtSlot()
    def on_openButton_clicked(self):
        self.image_path = easygui.fileopenbox()
        pix = QtGui.QPixmap(self.image_path)
        label = QtWidgets.QLabel(self.ui.beforeImage)
        label.setPixmap(pix.scaled(371, 441, QtCore.Qt.KeepAspectRatio))
        label.setScaledContents(True)
        label.show()

        self.change_state(RobotGuiState.IMAGE_LOADED)

    @pyqtSlot()
    def on_processButton_clicked(self):
        if self.image_path is not None:
            temp = cv2.imread(self.image_path, cv2.IMREAD_UNCHANGED)
            blur = cv2.blur(temp, (5, 5))
            canny = cv2.Canny(blur, 30, 150)

            self.contour_segments, _ = cv2.findContours(canny, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            cv2.drawContours(canny, self.contour_segments, -1, 255, 2)
            canny = 255 - canny
            cv2.imwrite('out.jpg', canny)

            pix = QtGui.QPixmap('out.jpg')
            lable = QtWidgets.QLabel(self.ui.afterImage)
            lable.setPixmap(pix.scaled(371, 441, QtCore.Qt.KeepAspectRatio))
            lable.setScaledContents(True)
            lable.show()

            self.contour_iter_prime = ContourIterator(self.contour_segments)

            print("Process Image")

            self.change_state(RobotGuiState.READY_TO_DRAW)

    @pyqtSlot()
    def on_tweakButton_clicked(self):
        print("Tweak Image")
        # TODO

    @pyqtSlot()
    def on_drawButton_clicked(self):
        print("Draw Image")

        if self.current_state == RobotGuiState.PAUSED:
            # Resume the drawing
            for device in self.esp_table:
                esp_wifi.send_mode_change(self, device.address, EspMode.DRAW)

        else:
            # Start the drawing
            arm1 = self.esp_table.get_device(1)
            points = self.contour_iter_prime.get_points(esp_wifi.POINT_TARGET_FILL)
            esp_wifi.send_points(self, arm1.address, points)
            esp_wifi.send_mode_change(self, arm1.address, EspMode.DRAW)

        self.change_state(RobotGuiState.DRAWING)

    @pyqtSlot()
    def on_pause_draw_button_clicked(self):
        for device in self.esp_table:
            esp_wifi.send_mode_change(self, device.address, EspMode.PAUSE)

        self.change_state(RobotGuiState.PAUSED)

    @pyqtSlot()
    def on_stop_draw_button_clicked(self):
        for device in self.esp_table:
            esp_wifi.send_mode_change(self, device.address, EspMode.IDLE)

        self.change_state(RobotGuiState.READY_TO_DRAW)


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)

    main_window = RobotMainWindow()

    main_window.show()
    sys.exit(app.exec_())
