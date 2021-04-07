# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'gui.ui'
#
# Created by: PyQt5 UI code generator 5.15.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1025, 598)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.left_column = QtWidgets.QVBoxLayout()
        self.left_column.setObjectName("left_column")
        self.image_grid = QtWidgets.QGridLayout()
        self.image_grid.setObjectName("image_grid")
        self.afterImage = QtWidgets.QGraphicsView(self.centralwidget)
        self.afterImage.setObjectName("afterImage")
        self.image_grid.addWidget(self.afterImage, 1, 1, 1, 1)
        self.label_4 = QtWidgets.QLabel(self.centralwidget)
        self.label_4.setAlignment(QtCore.Qt.AlignCenter)
        self.label_4.setObjectName("label_4")
        self.image_grid.addWidget(self.label_4, 2, 1, 1, 1)
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setAlignment(QtCore.Qt.AlignCenter)
        self.label_3.setObjectName("label_3")
        self.image_grid.addWidget(self.label_3, 2, 0, 1, 1)
        self.beforeImage = QtWidgets.QGraphicsView(self.centralwidget)
        self.beforeImage.setObjectName("beforeImage")
        self.image_grid.addWidget(self.beforeImage, 1, 0, 1, 1)
        self.left_column.addLayout(self.image_grid)
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.openButton = QtWidgets.QPushButton(self.centralwidget)
        self.openButton.setObjectName("openButton")
        self.gridLayout.addWidget(self.openButton, 0, 0, 1, 1)
        self.processButton = QtWidgets.QPushButton(self.centralwidget)
        self.processButton.setEnabled(False)
        self.processButton.setObjectName("processButton")
        self.gridLayout.addWidget(self.processButton, 0, 1, 1, 1)
        self.drawButton = QtWidgets.QPushButton(self.centralwidget)
        self.drawButton.setEnabled(False)
        self.drawButton.setObjectName("drawButton")
        self.gridLayout.addWidget(self.drawButton, 0, 2, 1, 1)
        self.pause_draw_button = QtWidgets.QPushButton(self.centralwidget)
        self.pause_draw_button.setEnabled(False)
        self.pause_draw_button.setObjectName("pause_draw_button")
        self.gridLayout.addWidget(self.pause_draw_button, 1, 1, 1, 1)
        self.stop_draw_button = QtWidgets.QPushButton(self.centralwidget)
        self.stop_draw_button.setEnabled(False)
        self.stop_draw_button.setObjectName("stop_draw_button")
        self.gridLayout.addWidget(self.stop_draw_button, 1, 2, 1, 1)
        self.left_column.addLayout(self.gridLayout)
        self.cTestButton = QtWidgets.QPushButton(self.centralwidget)
        self.cTestButton.setObjectName("cTestButton")
        self.left_column.addWidget(self.cTestButton)
        self.horizontalLayout.addLayout(self.left_column)
        self.esp_table_view = QtWidgets.QTableView(self.centralwidget)
        self.esp_table_view.setObjectName("esp_table_view")
        self.horizontalLayout.addWidget(self.esp_table_view)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1025, 26))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.label_4.setText(_translate("MainWindow", "Processed Image"))
        self.label_3.setText(_translate("MainWindow", "Original Image"))
        self.openButton.setText(_translate("MainWindow", "Open Image"))
        self.processButton.setText(_translate("MainWindow", "Process Image"))
        self.drawButton.setText(_translate("MainWindow", "Draw Image"))
        self.pause_draw_button.setText(_translate("MainWindow", "Pause Drawing"))
        self.stop_draw_button.setText(_translate("MainWindow", "Cancel Drawing"))
        self.cTestButton.setText(_translate("MainWindow", "Connection Test"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
