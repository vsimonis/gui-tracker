# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'NemPyTracker.ui'
#
# Created: Thu Jul 31 20:43:33 2014
#      by: PyQt5 UI code generator 5.3.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_TrackerUI(object):
    def setupUi(self, TrackerUI):
        TrackerUI.setObjectName("TrackerUI")
        TrackerUI.resize(1000, 700)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(TrackerUI.sizePolicy().hasHeightForWidth())
        TrackerUI.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(False)
        font.setWeight(50)
        TrackerUI.setFont(font)
        self.centralwidget = QtWidgets.QWidget(TrackerUI)
        self.centralwidget.setObjectName("centralwidget")
        self.wholeArea = QtWidgets.QWidget(self.centralwidget)
        self.wholeArea.setGeometry(QtCore.QRect(10, 0, 800, 650))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.wholeArea.setFont(font)
        self.wholeArea.setObjectName("wholeArea")
        self.topArea = QtWidgets.QWidget(self.wholeArea)
        self.topArea.setGeometry(QtCore.QRect(1, 1, 600, 50))
        self.topArea.setMaximumSize(QtCore.QSize(800, 16777215))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.topArea.setFont(font)
        self.topArea.setObjectName("topArea")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.topArea)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.studyControls = QtWidgets.QHBoxLayout()
        self.studyControls.setObjectName("studyControls")
        self.studyDesc = QtWidgets.QLabel(self.topArea)
        self.studyDesc.setMaximumSize(QtCore.QSize(50, 16777215))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.studyDesc.setFont(font)
        self.studyDesc.setObjectName("studyDesc")
        self.studyControls.addWidget(self.studyDesc)
        self.studyName = QtWidgets.QLineEdit(self.topArea)
        self.studyName.setMinimumSize(QtCore.QSize(200, 0))
        self.studyName.setMaximumSize(QtCore.QSize(200, 16777215))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.studyName.setFont(font)
        self.studyName.setObjectName("studyName")
        self.studyControls.addWidget(self.studyName)
        self.horizontalLayout.addLayout(self.studyControls)
        self.srcControls = QtWidgets.QHBoxLayout()
        self.srcControls.setObjectName("srcControls")
        self.srcDesc = QtWidgets.QLabel(self.topArea)
        self.srcDesc.setMaximumSize(QtCore.QSize(50, 16777215))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.srcDesc.setFont(font)
        self.srcDesc.setObjectName("srcDesc")
        self.srcControls.addWidget(self.srcDesc)
        self.srcCombo = QtWidgets.QComboBox(self.topArea)
        self.srcCombo.setMinimumSize(QtCore.QSize(200, 0))
        self.srcCombo.setMaximumSize(QtCore.QSize(200, 16777215))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.srcCombo.setFont(font)
        self.srcCombo.setObjectName("srcCombo")
        self.srcControls.addWidget(self.srcCombo)
        self.horizontalLayout.addLayout(self.srcControls)
        self.videoFrame = QtWidgets.QLabel(self.wholeArea)
        self.videoFrame.setGeometry(QtCore.QRect(2, 48, 800, 600))
        self.videoFrame.setMinimumSize(QtCore.QSize(640, 480))
        self.videoFrame.setMaximumSize(QtCore.QSize(800, 600))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.videoFrame.setFont(font)
        self.videoFrame.setAlignment(QtCore.Qt.AlignCenter)
        self.videoFrame.setObjectName("videoFrame")
        self.controls = QtWidgets.QWidget(self.centralwidget)
        self.controls.setGeometry(QtCore.QRect(830, 50, 150, 600))
        self.controls.setObjectName("controls")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.controls)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.buttonConnect = QtWidgets.QPushButton(self.controls)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.buttonConnect.setFont(font)
        self.buttonConnect.setObjectName("buttonConnect")
        self.verticalLayout.addWidget(self.buttonConnect)
        self.line_6 = QtWidgets.QFrame(self.controls)
        self.line_6.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_6.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_6.setObjectName("line_6")
        self.verticalLayout.addWidget(self.line_6)
        self.buttonRun = QtWidgets.QPushButton(self.controls)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.buttonRun.setFont(font)
        self.buttonRun.setObjectName("buttonRun")
        self.verticalLayout.addWidget(self.buttonRun)
        self.buttonRefresh = QtWidgets.QPushButton(self.controls)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.buttonRefresh.setFont(font)
        self.buttonRefresh.setObjectName("buttonRefresh")
        self.verticalLayout.addWidget(self.buttonRefresh)
        self.line = QtWidgets.QFrame(self.controls)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.line.setFont(font)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.verticalLayout.addWidget(self.line)
        self.scaling = QtWidgets.QLabel(self.controls)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.scaling.setFont(font)
        self.scaling.setAlignment(QtCore.Qt.AlignCenter)
        self.scaling.setObjectName("scaling")
        self.verticalLayout.addWidget(self.scaling)
        self.scalingSlider = QtWidgets.QSlider(self.controls)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.scalingSlider.setFont(font)
        self.scalingSlider.setMinimum(1)
        self.scalingSlider.setMaximum(30)
        self.scalingSlider.setOrientation(QtCore.Qt.Horizontal)
        self.scalingSlider.setObjectName("scalingSlider")
        self.verticalLayout.addWidget(self.scalingSlider)
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.buttonUp = QtWidgets.QPushButton(self.controls)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.buttonUp.setFont(font)
        self.buttonUp.setObjectName("buttonUp")
        self.gridLayout.addWidget(self.buttonUp, 0, 1, 1, 1)
        self.buttonLeft = QtWidgets.QPushButton(self.controls)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.buttonLeft.setFont(font)
        self.buttonLeft.setObjectName("buttonLeft")
        self.gridLayout.addWidget(self.buttonLeft, 1, 0, 1, 1)
        self.buttonRight = QtWidgets.QPushButton(self.controls)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.buttonRight.setFont(font)
        self.buttonRight.setObjectName("buttonRight")
        self.gridLayout.addWidget(self.buttonRight, 1, 2, 1, 1)
        self.buttonDown = QtWidgets.QPushButton(self.controls)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.buttonDown.setFont(font)
        self.buttonDown.setObjectName("buttonDown")
        self.gridLayout.addWidget(self.buttonDown, 2, 1, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.line_2 = QtWidgets.QFrame(self.controls)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.line_2.setFont(font)
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.verticalLayout.addWidget(self.line_2)
        self.motorsDesc = QtWidgets.QLabel(self.controls)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.motorsDesc.setFont(font)
        self.motorsDesc.setAlignment(QtCore.Qt.AlignCenter)
        self.motorsDesc.setObjectName("motorsDesc")
        self.verticalLayout.addWidget(self.motorsDesc)
        self.buttonMotorized = QtWidgets.QPushButton(self.controls)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.buttonMotorized.setFont(font)
        self.buttonMotorized.setObjectName("buttonMotorized")
        self.verticalLayout.addWidget(self.buttonMotorized)
        self.line_3 = QtWidgets.QFrame(self.controls)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.line_3.setFont(font)
        self.line_3.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_3.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_3.setObjectName("line_3")
        self.verticalLayout.addWidget(self.line_3)
        self.recordingDesc = QtWidgets.QLabel(self.controls)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.recordingDesc.setFont(font)
        self.recordingDesc.setAlignment(QtCore.Qt.AlignCenter)
        self.recordingDesc.setObjectName("recordingDesc")
        self.verticalLayout.addWidget(self.recordingDesc)
        self.buttonRec = QtWidgets.QPushButton(self.controls)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.buttonRec.setFont(font)
        self.buttonRec.setObjectName("buttonRec")
        self.verticalLayout.addWidget(self.buttonRec)
        self.line_4 = QtWidgets.QFrame(self.controls)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.line_4.setFont(font)
        self.line_4.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_4.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_4.setObjectName("line_4")
        self.verticalLayout.addWidget(self.line_4)
        self.fps = QtWidgets.QLabel(self.controls)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.fps.setFont(font)
        self.fps.setObjectName("fps")
        self.verticalLayout.addWidget(self.fps)
        self.lcdNumber = QtWidgets.QLCDNumber(self.controls)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.lcdNumber.setFont(font)
        self.lcdNumber.setObjectName("lcdNumber")
        self.verticalLayout.addWidget(self.lcdNumber)
        self.line_5 = QtWidgets.QFrame(self.controls)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.line_5.setFont(font)
        self.line_5.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_5.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_5.setObjectName("line_5")
        self.verticalLayout.addWidget(self.line_5)
        self.buttonReset = QtWidgets.QPushButton(self.controls)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.buttonReset.setFont(font)
        self.buttonReset.setObjectName("buttonReset")
        self.verticalLayout.addWidget(self.buttonReset)
        TrackerUI.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(TrackerUI)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1000, 28))
        self.menubar.setObjectName("menubar")
        TrackerUI.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(TrackerUI)
        self.statusbar.setObjectName("statusbar")
        TrackerUI.setStatusBar(self.statusbar)

        self.retranslateUi(TrackerUI)
        QtCore.QMetaObject.connectSlotsByName(TrackerUI)

    def retranslateUi(self, TrackerUI):
        _translate = QtCore.QCoreApplication.translate
        TrackerUI.setWindowTitle(_translate("TrackerUI", "NemPy Tracker"))
        self.studyDesc.setText(_translate("TrackerUI", "Study"))
        self.srcDesc.setText(_translate("TrackerUI", "Source"))
        self.videoFrame.setText(_translate("TrackerUI", "Select source to see video here"))
        self.buttonConnect.setText(_translate("TrackerUI", "Connect Motors"))
        self.buttonRun.setText(_translate("TrackerUI", "Run Finder"))
        self.buttonRefresh.setText(_translate("TrackerUI", "Refresh Ref"))
        self.scaling.setText(_translate("TrackerUI", "TextLabel"))
        self.buttonUp.setText(_translate("TrackerUI", "Up"))
        self.buttonLeft.setText(_translate("TrackerUI", "Left"))
        self.buttonRight.setText(_translate("TrackerUI", "Right"))
        self.buttonDown.setText(_translate("TrackerUI", "Down"))
        self.motorsDesc.setText(_translate("TrackerUI", "Motorized"))
        self.buttonMotorized.setText(_translate("TrackerUI", "On"))
        self.recordingDesc.setText(_translate("TrackerUI", "Recording"))
        self.buttonRec.setText(_translate("TrackerUI", "Start"))
        self.fps.setText(_translate("TrackerUI", "TextLabel"))
        self.buttonReset.setText(_translate("TrackerUI", "Reset"))

