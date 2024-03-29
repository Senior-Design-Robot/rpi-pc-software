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
        self.leftColumn = QtWidgets.QVBoxLayout()
        self.leftColumn.setObjectName("leftColumn")
        self.imageGrid = QtWidgets.QGridLayout()
        self.imageGrid.setObjectName("imageGrid")
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setAlignment(QtCore.Qt.AlignCenter)
        self.label_3.setObjectName("label_3")
        self.imageGrid.addWidget(self.label_3, 2, 0, 1, 1)
        self.label_4 = QtWidgets.QLabel(self.centralwidget)
        self.label_4.setAlignment(QtCore.Qt.AlignCenter)
        self.label_4.setObjectName("label_4")
        self.imageGrid.addWidget(self.label_4, 2, 1, 1, 1)
        self.afterImage = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.afterImage.sizePolicy().hasHeightForWidth())
        self.afterImage.setSizePolicy(sizePolicy)
        self.afterImage.setText("")
        self.afterImage.setAlignment(QtCore.Qt.AlignCenter)
        self.afterImage.setObjectName("afterImage")
        self.imageGrid.addWidget(self.afterImage, 1, 1, 1, 1)
        self.beforeImage = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.beforeImage.sizePolicy().hasHeightForWidth())
        self.beforeImage.setSizePolicy(sizePolicy)
        self.beforeImage.setText("")
        self.beforeImage.setAlignment(QtCore.Qt.AlignCenter)
        self.beforeImage.setObjectName("beforeImage")
        self.imageGrid.addWidget(self.beforeImage, 1, 0, 1, 1)
        self.leftColumn.addLayout(self.imageGrid)
        self.drawScaleGroup = QtWidgets.QGroupBox(self.centralwidget)
        self.drawScaleGroup.setEnabled(False)
        self.drawScaleGroup.setObjectName("drawScaleGroup")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.drawScaleGroup)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.label = QtWidgets.QLabel(self.drawScaleGroup)
        self.label.setObjectName("label")
        self.gridLayout_3.addWidget(self.label, 1, 0, 1, 1)
        self.label_2 = QtWidgets.QLabel(self.drawScaleGroup)
        self.label_2.setObjectName("label_2")
        self.gridLayout_3.addWidget(self.label_2, 1, 2, 1, 1)
        self.label_6 = QtWidgets.QLabel(self.drawScaleGroup)
        self.label_6.setObjectName("label_6")
        self.gridLayout_3.addWidget(self.label_6, 2, 2, 1, 1)
        self.hOffsetSpin = QtWidgets.QDoubleSpinBox(self.drawScaleGroup)
        self.hOffsetSpin.setSuffix(" in")
        self.hOffsetSpin.setMinimum(-10.0)
        self.hOffsetSpin.setMaximum(10.0)
        self.hOffsetSpin.setSingleStep(0.5)
        self.hOffsetSpin.setObjectName("hOffsetSpin")
        self.gridLayout_3.addWidget(self.hOffsetSpin, 1, 3, 1, 1)
        self.vOffsetSpin = QtWidgets.QDoubleSpinBox(self.drawScaleGroup)
        self.vOffsetSpin.setSuffix(" in")
        self.vOffsetSpin.setMaximum(20.0)
        self.vOffsetSpin.setSingleStep(0.5)
        self.vOffsetSpin.setObjectName("vOffsetSpin")
        self.gridLayout_3.addWidget(self.vOffsetSpin, 2, 3, 1, 1)
        self.hScaleSpin = QtWidgets.QDoubleSpinBox(self.drawScaleGroup)
        self.hScaleSpin.setSuffix(" in")
        self.hScaleSpin.setMaximum(15.0)
        self.hScaleSpin.setSingleStep(0.5)
        self.hScaleSpin.setObjectName("hScaleSpin")
        self.gridLayout_3.addWidget(self.hScaleSpin, 1, 1, 1, 1)
        self.vScaleSpin = QtWidgets.QDoubleSpinBox(self.drawScaleGroup)
        self.vScaleSpin.setSuffix(" in")
        self.vScaleSpin.setMaximum(15.0)
        self.vScaleSpin.setSingleStep(0.5)
        self.vScaleSpin.setObjectName("vScaleSpin")
        self.gridLayout_3.addWidget(self.vScaleSpin, 2, 1, 1, 1)
        self.label_5 = QtWidgets.QLabel(self.drawScaleGroup)
        self.label_5.setObjectName("label_5")
        self.gridLayout_3.addWidget(self.label_5, 2, 0, 1, 1)
        self.imgSizeLabel = QtWidgets.QLabel(self.drawScaleGroup)
        self.imgSizeLabel.setObjectName("imgSizeLabel")
        self.gridLayout_3.addWidget(self.imgSizeLabel, 0, 0, 1, 1)
        self.leftColumn.addWidget(self.drawScaleGroup)
        self.drawControlGroup = QtWidgets.QGroupBox(self.centralwidget)
        self.drawControlGroup.setObjectName("drawControlGroup")
        self.gridLayout = QtWidgets.QGridLayout(self.drawControlGroup)
        self.gridLayout.setObjectName("gridLayout")
        self.processButton = QtWidgets.QPushButton(self.drawControlGroup)
        self.processButton.setEnabled(False)
        self.processButton.setObjectName("processButton")
        self.gridLayout.addWidget(self.processButton, 0, 1, 1, 1)
        self.openButton = QtWidgets.QPushButton(self.drawControlGroup)
        self.openButton.setObjectName("openButton")
        self.gridLayout.addWidget(self.openButton, 0, 0, 1, 1)
        self.pauseButton = QtWidgets.QPushButton(self.drawControlGroup)
        self.pauseButton.setEnabled(False)
        self.pauseButton.setObjectName("pauseButton")
        self.gridLayout.addWidget(self.pauseButton, 1, 1, 1, 1)
        self.stopButton = QtWidgets.QPushButton(self.drawControlGroup)
        self.stopButton.setEnabled(False)
        self.stopButton.setObjectName("stopButton")
        self.gridLayout.addWidget(self.stopButton, 1, 2, 1, 1)
        self.drawButton = QtWidgets.QPushButton(self.drawControlGroup)
        self.drawButton.setEnabled(False)
        self.drawButton.setObjectName("drawButton")
        self.gridLayout.addWidget(self.drawButton, 0, 2, 1, 1)
        self.openGcodeButton = QtWidgets.QPushButton(self.drawControlGroup)
        self.openGcodeButton.setObjectName("openGcodeButton")
        self.gridLayout.addWidget(self.openGcodeButton, 1, 0, 1, 1)
        self.elapsedTimeLabel = QtWidgets.QLabel(self.drawControlGroup)
        self.elapsedTimeLabel.setObjectName("elapsedTimeLabel")
        self.gridLayout.addWidget(self.elapsedTimeLabel, 2, 2, 1, 1)
        self.label_8 = QtWidgets.QLabel(self.drawControlGroup)
        self.label_8.setObjectName("label_8")
        self.gridLayout.addWidget(self.label_8, 2, 1, 1, 1)
        self.singleArmCheck = QtWidgets.QCheckBox(self.drawControlGroup)
        self.singleArmCheck.setObjectName("singleArmCheck")
        self.gridLayout.addWidget(self.singleArmCheck, 2, 0, 1, 1)
        self.leftColumn.addWidget(self.drawControlGroup)
        self.horizontalLayout.addLayout(self.leftColumn)
        self.espTableView = QtWidgets.QTableView(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.espTableView.sizePolicy().hasHeightForWidth())
        self.espTableView.setSizePolicy(sizePolicy)
        self.espTableView.setObjectName("espTableView")
        self.horizontalLayout.addWidget(self.espTableView)
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
        self.label_3.setText(_translate("MainWindow", "Original Image"))
        self.label_4.setText(_translate("MainWindow", "Processed Image"))
        self.drawScaleGroup.setTitle(_translate("MainWindow", "Drawing Properties"))
        self.label.setText(_translate("MainWindow", "Horizontal Scale:"))
        self.label_2.setText(_translate("MainWindow", "Horizontal Offset:"))
        self.label_6.setText(_translate("MainWindow", "Bottom Offset:"))
        self.label_5.setText(_translate("MainWindow", "Vertical Scale:"))
        self.imgSizeLabel.setText(_translate("MainWindow", "Image Size: N/A"))
        self.drawControlGroup.setTitle(_translate("MainWindow", "Drawing Controls"))
        self.processButton.setText(_translate("MainWindow", "Process Image"))
        self.openButton.setText(_translate("MainWindow", "Open Image..."))
        self.pauseButton.setText(_translate("MainWindow", "Pause Drawing"))
        self.stopButton.setText(_translate("MainWindow", "Cancel Drawing"))
        self.drawButton.setText(_translate("MainWindow", "Draw Image"))
        self.openGcodeButton.setText(_translate("MainWindow", "Open GCode File..."))
        self.elapsedTimeLabel.setText(_translate("MainWindow", "0 min, 0 sec"))
        self.label_8.setText(_translate("MainWindow", "Elapsed Time:"))
        self.singleArmCheck.setText(_translate("MainWindow", "Single Arm Mode"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
