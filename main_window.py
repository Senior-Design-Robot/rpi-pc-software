from enum import IntEnum
from typing import Optional, Dict

import cv2
import easygui
import numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets, QtNetwork
from PyQt5.QtCore import pyqtSlot, QTime

import esp_status
from esp_status import EspMode
import esp_wifi
from contour_iterator import ContourIterator
from gcode_decode import GCodeIterator, load_gcode_commands, get_contours_from_path
from gui import Ui_MainWindow
from point_ops import AbstractPointIterator

main_window = None  # type: Optional[QtWidgets.QMainWindow]


class RobotGuiState(IntEnum):
    NO_IMAGE = 0
    IMAGE_LOADED = 1
    READY_TO_DRAW = 2
    DRAWING = 3
    PAUSED = 4


MAX_IMG_SCALE = 11.0


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

            # update elapsed time
            self.draw_complete_time = QTime.currentTime()
            elapsed = self.draw_start_time.secsTo(self.draw_complete_time)
            self.ui.elapsedTimeLabel.setText(f"{int(elapsed / 60)} min, {elapsed % 60} sec")

            draw_queue = self.contour_iter_prime if (device.dev_id == 1) else self.contour_iter_second

            if draw_queue and not draw_queue.is_empty:
                if (esp_wifi.POINT_TARGET_FILL - device.points_left) > esp_wifi.POINT_XMIT_THRESHOLD:
                    points = draw_queue.get_points(esp_wifi.POINT_XMIT_THRESHOLD)

                    port = 1897 if (device.dev_id == 1) else 1898
                    esp_wifi.send_points(self, device.address, port, points)

    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # setup slots
        self.ui.openButton.clicked.connect(self.openButton_clicked)
        self.ui.openGcodeButton.clicked.connect(self.openGcodeButton_clicked)
        self.ui.processButton.clicked.connect(self.processButton_clicked)
        self.ui.drawButton.clicked.connect(self.drawButton_clicked)
        self.ui.pauseButton.clicked.connect(self.pauseButton_clicked)
        self.ui.stopButton.clicked.connect(self.stopButton_clicked)

        self.ui.hScaleSpin.valueChanged.connect(self.hScaleSpin_valueChanged)
        self.ui.vScaleSpin.valueChanged.connect(self.vScaleSpin_valueChanged)
        self.ui.singleArmCheck.stateChanged.connect(self.singleArmCheck_stateChanged)

        self.image_path = None
        self.contour_segments = None
        self.contour_segments_arm_1 = []
        self.contour_segments_arm_2 = []
        self.contour_iter_prime = None  # type: Optional[AbstractPointIterator]
        self.contour_iter_second = None  # type: Optional[AbstractPointIterator]
        self.draw_start_time = QTime.currentTime()
        self.draw_complete_time = self.draw_start_time

        self.current_state = RobotGuiState.NO_IMAGE
        self.single_arm = False

        self.img_shape = (0, 0)
        self.changing_scale = False

        self.esp_table = esp_status.DeviceTable(self)
        self.esp_table.device_modified.connect(self.esp_status_changed)
        self.ui.espTableView.setModel(self.esp_table)
        self.ui.espTableView.show()

        self.sockets = []
        self.server = QtNetwork.QTcpServer(self)
        self.server.newConnection.connect(self.handle_new_connection)
        self.server.listen(QtNetwork.QHostAddress.AnyIPv4, esp_wifi.SERV_PORT)

        self.change_state(RobotGuiState.NO_IMAGE)

    @property
    def img_height(self):
        return self.img_shape[0]

    @property
    def img_width(self):
        return self.img_shape[1]

    def change_state(self, new_state: RobotGuiState):
        self.current_state = new_state

        if new_state == RobotGuiState.NO_IMAGE:
            self.ui.processButton.setEnabled(False)
            self.ui.drawButton.setEnabled(False)
            self.ui.pauseButton.setEnabled(False)
            self.ui.stopButton.setEnabled(False)
            self.ui.drawScaleGroup.setEnabled(False)

        elif new_state == RobotGuiState.IMAGE_LOADED:
            self.ui.processButton.setEnabled(True)
            self.ui.drawButton.setEnabled(False)
            self.ui.pauseButton.setEnabled(False)
            self.ui.stopButton.setEnabled(False)
            self.ui.drawScaleGroup.setEnabled(True)

        elif new_state == RobotGuiState.READY_TO_DRAW:
            self.ui.processButton.setEnabled(self.image_path is not None)
            self.ui.drawButton.setEnabled(not self.esp_table.is_empty)
            self.ui.pauseButton.setEnabled(False)
            self.ui.stopButton.setEnabled(False)
            self.ui.drawScaleGroup.setEnabled(True)

        elif new_state == RobotGuiState.DRAWING:
            self.ui.processButton.setEnabled(False)
            self.ui.drawButton.setEnabled(False)
            self.ui.pauseButton.setEnabled(True)
            self.ui.stopButton.setEnabled(True)
            self.ui.drawScaleGroup.setEnabled(True)

        elif new_state == RobotGuiState.PAUSED:
            self.ui.processButton.setEnabled(False)
            self.ui.drawButton.setEnabled(True)
            self.ui.pauseButton.setEnabled(True)
            self.ui.stopButton.setEnabled(True)
            self.ui.drawScaleGroup.setEnabled(True)

    def drawing_finished(self):
        self.draw_complete_time = QTime.currentTime()
        elapsed = self.draw_start_time.secsTo(self.draw_complete_time)
        self.ui.elapsedTimeLabel.setText(f"{int(elapsed / 60)} min, {elapsed % 60} sec")

        if self.contour_iter_prime:
            self.contour_iter_prime.reset()

        if self.contour_iter_second:
            self.contour_iter_second.reset()

        self.change_state(RobotGuiState.READY_TO_DRAW)

    @pyqtSlot()
    def openButton_clicked(self):
        self.image_path = easygui.fileopenbox()
        pix = QtGui.QPixmap(self.image_path)

        self.img_shape = (pix.size().height(), pix.size().width())
        self.ui.imgSizeLabel.setText(f"Image Size: {self.img_width}w x {self.img_height}h")

        label = self.ui.beforeImage
        label.setPixmap(pix.scaled(label.size(), QtCore.Qt.KeepAspectRatio))

        self.change_state(RobotGuiState.IMAGE_LOADED)

    @pyqtSlot()
    def openGcodeButton_clicked(self):
        self.image_path = None
        gcode_path = easygui.fileopenbox(title="Open GCode", filetypes=[["*.gcode", "GCode Files"]])

        try:
            commands, max_x, max_y = load_gcode_commands(gcode_path)
            self.contour_iter_prime = GCodeIterator(commands, max_x, max_y)

            self.img_shape = (max_y, max_x)
            self.ui.imgSizeLabel.setText(f"Image Size: {self.img_width}w x {self.img_height}h")

            self.contour_segments, width, height = get_contours_from_path(commands, max_x, max_y)
            contour_img = np.full((height, width, 3), 255, np.uint8)
            cv2.drawContours(contour_img, self.contour_segments, -1, (0, 0, 0), 5)
            cv2.imwrite('out.png', contour_img)

            q_pix = QtGui.QPixmap('out.png')
            self.ui.afterImage.setPixmap(q_pix.scaled(self.ui.afterImage.size(), QtCore.Qt.KeepAspectRatio))

            self.contour_segments_arm_1.clear()
            self.contour_segments_arm_2.clear()

            if self.single_arm:
                self.contour_iter_prime = ContourIterator(self.contour_segments, width, height)
                self.contour_iter_second = None
                self.change_state(RobotGuiState.READY_TO_DRAW)
                return

            for i in range(0, len(self.contour_segments)):
                above = 0
                below = 0

                contour = self.contour_segments[i]
                for point in contour:
                    point = point[0]
                    if point[0] < width / 2:
                        below += 1
                    else:
                        above += 1

                if above > below:
                    self.contour_segments_arm_2.append(contour)
                else:
                    self.contour_segments_arm_1.append(contour)

            self.contour_iter_prime = ContourIterator(self.contour_segments_arm_1, width, height)
            self.contour_iter_second = ContourIterator(self.contour_segments_arm_2, width, height)

            self.change_state(RobotGuiState.READY_TO_DRAW)

        except FileNotFoundError:
            easygui.msgbox("Could not open gcode file", "IO Error")
            return

    @pyqtSlot()
    def processButton_clicked(self):
        if self.image_path is not None:

            print("Process Image")

            temp = cv2.imread(self.image_path, cv2.IMREAD_UNCHANGED)

            blur = cv2.blur(temp, (5, 5))
            canny = cv2.Canny(blur, 30, 150)

            self.contour_segments, _ = cv2.findContours(canny, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            cv2.drawContours(canny, self.contour_segments, -1, 255, 2)
            canny = 255 - canny
            cv2.imwrite('out.jpg', canny)

            pix = QtGui.QPixmap('out.jpg')
            # lable = QtWidgets.QLabel(self.ui.afterImage)
            label = self.ui.afterImage
            label.setPixmap(pix.scaled(label.size(), QtCore.Qt.KeepAspectRatio))

            self.contour_segments_arm_1.clear()
            self.contour_segments_arm_2.clear()

            if self.single_arm:
                self.contour_iter_prime = ContourIterator(self.contour_segments, self.img_width, self.img_height)
                self.contour_iter_second = None
                self.change_state(RobotGuiState.READY_TO_DRAW)
                return

            # determine which arm each contour belongs to
            # print(np.squeeze(self.contour_segments).toList())
            for i in range(0, len(self.contour_segments)):
                above = 0
                below = 0

                contour = self.contour_segments[i]
                for point in contour:
                    point = point[0]
                    if point[0] < self.img_width / 2:
                        below += 1
                    else:
                        above += 1

                if above > below:
                    self.contour_segments_arm_2.append(contour)
                else:
                    self.contour_segments_arm_1.append(contour)

            self.contour_iter_prime = ContourIterator(self.contour_segments_arm_1, self.img_width, self.img_height)
            self.contour_iter_second = ContourIterator(self.contour_segments_arm_2, self.img_width, self.img_height)

            self.change_state(RobotGuiState.READY_TO_DRAW)

    @pyqtSlot()
    def drawButton_clicked(self):
        print("Draw Image")

        if self.current_state == RobotGuiState.PAUSED:
            # Resume the drawing
            for device in self.esp_table:
                if device.mode == EspMode.PAUSE:
                    port = 1897 if (device.dev_id == 1) else 1898
                    esp_wifi.send_mode_change(self, device.address, port, EspMode.DRAW)

        else:
            # Start the drawing
            self.draw_start_time = QTime.currentTime()

            if self.contour_iter_prime:
                arm1 = self.esp_table.get_device(1)

                self.contour_iter_prime.set_scale(self.ui.hScaleSpin.value() * 2.54)
                self.contour_iter_prime.set_offset(self.ui.hOffsetSpin.value() * 2.54, self.ui.vOffsetSpin.value() * 2.54)
                points = self.contour_iter_prime.get_points(esp_wifi.POINT_TARGET_FILL)

                if len(points) > 0:
                    esp_wifi.send_points(self, arm1.address, 1897, points)
                    esp_wifi.send_mode_change(self, arm1.address, 1897, EspMode.DRAW)
            
            # second arm
            if not self.single_arm and self.contour_iter_second:
                arm2 = self.esp_table.get_device(2)

                self.contour_iter_second.set_scale(self.ui.hScaleSpin.value() * 2.54)
                self.contour_iter_second.set_offset(self.ui.hOffsetSpin.value() * 2.54, self.ui.vOffsetSpin.value() * 2.54)
                points2 = self.contour_iter_second.get_points(esp_wifi.POINT_TARGET_FILL)

                if len(points2) > 0:
                    esp_wifi.send_points(self, arm2.address, 1898, points2)
                    esp_wifi.send_mode_change(self, arm2.address, 1898, EspMode.DRAW)

        self.change_state(RobotGuiState.DRAWING)

    @pyqtSlot()
    def pauseButton_clicked(self):
        for device in self.esp_table:
            port = 1897 if (device.dev_id == 1) else 1898
            esp_wifi.send_mode_change(self, device.address, port, EspMode.PAUSE)

        self.change_state(RobotGuiState.PAUSED)

    @pyqtSlot()
    def stopButton_clicked(self):
        for device in self.esp_table:
            port = 1897 if (device.dev_id == 1) else 1898
            esp_wifi.send_mode_change(self, device.address, port, EspMode.IDLE)

        self.drawing_finished()

    @pyqtSlot('double')
    def hScaleSpin_valueChanged(self, d: float):
        if not self.changing_scale:
            self.changing_scale = True
            new_height = d * self.img_height / self.img_width

            if new_height > MAX_IMG_SCALE:
                self.ui.hScaleSpin.setValue(MAX_IMG_SCALE * self.img_width / self.img_height)
                new_height = MAX_IMG_SCALE

            self.ui.vScaleSpin.setValue(new_height)
            self.changing_scale = False

    @pyqtSlot('double')
    def vScaleSpin_valueChanged(self, d: float):
        if not self.changing_scale:
            self.changing_scale = True
            new_width = d * self.img_width / self.img_height

            if new_width > MAX_IMG_SCALE:
                self.ui.vScaleSpin.setValue(MAX_IMG_SCALE * self.img_height / self.img_width)
                new_width = MAX_IMG_SCALE

            self.ui.hScaleSpin.setValue(new_width)
            self.changing_scale = False

    @pyqtSlot('int')
    def singleArmCheck_stateChanged(self, state: int):
        self.single_arm = self.ui.singleArmCheck.isChecked()
        self.change_state(RobotGuiState.NO_IMAGE)
        self.ui.afterImage.clear()


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)

    main_window = RobotMainWindow()

    main_window.show()
    sys.exit(app.exec_())
