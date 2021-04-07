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


class RobotMainWindow(QtWidgets.QMainWindow):
    @pyqtSlot()
    def handle_new_connection(self):
        while self.server.hasPendingConnections():
            client = self.server.nextPendingConnection()
            # print(f"New connection from {client.peerAddress().toString()}")
            esp_wifi.ReceiveWrapper(self, client, self.esp_table)

    @pyqtSlot(esp_status.EspStatus)
    def esp_status_changed(self, device: esp_status.EspStatus):
        self.change_state(self.current_state)  # refresh buttons

        if self.current_state == RobotGuiState.DRAWING:
            # check if devices finished drawing
            if device.mode == EspMode.IDLE:
                if all([(d.mode == EspMode.IDLE) for d in self.esp_table]):
                    self.drawing_finished()
                    return

            draw_queue = self.contour_iter_prime if (device.dev_id == 1) else self.contour_iter_second

            if not draw_queue.is_empty:
                if (esp_wifi.POINT_TARGET_FILL - device.points_left) > esp_wifi.POINT_XMIT_THRESHOLD:
                    points = self.contour_iter_prime.get_points(esp_wifi.POINT_XMIT_THRESHOLD)
                    esp_wifi.send_points(self, device.address, points)

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
        self.current_state = new_state

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

    def drawing_finished(self):
        if self.contour_iter_prime:
            self.contour_iter_prime.reset()

        if self.contour_iter_second:
            self.contour_iter_second.reset()

        self.change_state(RobotGuiState.READY_TO_DRAW)

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

        self.drawing_finished()


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)

    main_window = RobotMainWindow()

    main_window.show()
    sys.exit(app.exec_())
