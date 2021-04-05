from typing import Optional

import cv2
import easygui
from PyQt5 import QtCore, QtGui, QtWidgets, QtNetwork
from PyQt5.QtCore import pyqtSlot

from contour_iterator import ContourIterator
from gui import Ui_MainWindow
import esp_wifi

ui = None  # type: Optional[Ui_MainWindow]
main_window = None  # type: Optional[QtWidgets.QMainWindow]


class RobotMainWindow(QtWidgets.QMainWindow):
    def handle_new_connection(self):
        if self.server.hasPendingConnections():
            client = self.server.nextPendingConnection()
            print(f"New connection from {client.peerAddress()}")

            read_data = client.read(1024)
            esp_wifi.handle_packet(read_data, client.peerAddress().toString())

        else:
            print("What? the connection disappeared :(")

    def __init__(self):
        super().__init__()
        self.image_path = None
        self.contour_segments = None
        self.contour_iter = None  # type: Optional[ContourIterator]

        self.server = QtNetwork.QTcpServer(self)
        self.server.newConnection.connect(self.handle_new_connection)
        self.server.listen(QtNetwork.QHostAddress.Any, esp_wifi.SERV_PORT)

    @pyqtSlot()
    def on_cTestButton_clicked(self):
        print("Connection Test")
        # TODO

    @pyqtSlot()
    def on_openButton_clicked(self):
        self.image_path = easygui.fileopenbox()
        pix = QtGui.QPixmap(self.image_path)
        label = QtWidgets.QLabel(ui.beforeImage)
        label.setPixmap(pix.scaled(371, 441, QtCore.Qt.KeepAspectRatio))
        label.setScaledContents(True)
        label.show()

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
            lable = QtWidgets.QLabel(ui.afterImage)
            lable.setPixmap(pix.scaled(371, 441, QtCore.Qt.KeepAspectRatio))
            lable.setScaledContents(True)
            lable.show()
            print("Process Image")

    @pyqtSlot()
    def on_tweakButton_clicked(self):
        print("Tweak Image")
        # TODO

    @pyqtSlot()
    def on_drawButton_clicked(self):
        print("Draw Image")

        self.contour_iter = ContourIterator(self.contour_segments)


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)

    main_window = RobotMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(main_window)

    main_window.show()
    sys.exit(app.exec_())
