# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\ui\unote_gui.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1680, 1027)
        MainWindow.setToolTipDuration(5)
        MainWindow.setIconSize(QtCore.QSize(64, 64))
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.verticalLayout_6.addLayout(self.gridLayout)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1680, 21))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuTools = QtWidgets.QMenu(self.menubar)
        self.menuTools.setObjectName("menuTools")
        MainWindow.setMenuBar(self.menubar)
        self.actionExit = QtWidgets.QAction(MainWindow)
        self.actionExit.setCheckable(False)
        self.actionExit.setObjectName("actionExit")
        self.actionPreferences = QtWidgets.QAction(MainWindow)
        self.actionPreferences.setObjectName("actionPreferences")
        self.actionLoad_PDF = QtWidgets.QAction(MainWindow)
        self.actionLoad_PDF.setObjectName("actionLoad_PDF")
        self.actionText_Mode = QtWidgets.QAction(MainWindow)
        self.actionText_Mode.setCheckable(True)
        self.actionText_Mode.setObjectName("actionText_Mode")
        self.actionHighlight_Mode = QtWidgets.QAction(MainWindow)
        self.actionHighlight_Mode.setCheckable(True)
        self.actionHighlight_Mode.setObjectName("actionHighlight_Mode")
        self.actionSave_PDF = QtWidgets.QAction(MainWindow)
        self.actionSave_PDF.setObjectName("actionSave_PDF")
        self.menuFile.addAction(self.actionLoad_PDF)
        self.menuFile.addAction(self.actionSave_PDF)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionPreferences)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionExit)
        self.menuTools.addAction(self.actionText_Mode)
        self.menuTools.addAction(self.actionHighlight_Mode)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuTools.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "UNote"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.menuTools.setTitle(_translate("MainWindow", "Tools"))
        self.actionExit.setText(_translate("MainWindow", "Exit"))
        self.actionExit.setShortcut(_translate("MainWindow", "Esc"))
        self.actionPreferences.setText(_translate("MainWindow", "Preferences"))
        self.actionPreferences.setShortcut(_translate("MainWindow", "Ctrl+P"))
        self.actionLoad_PDF.setText(_translate("MainWindow", "Load PDF"))
        self.actionLoad_PDF.setShortcut(_translate("MainWindow", "Ctrl+O"))
        self.actionText_Mode.setText(_translate("MainWindow", "Text Mode"))
        self.actionText_Mode.setShortcut(_translate("MainWindow", "Ctrl+T"))
        self.actionHighlight_Mode.setText(_translate("MainWindow", "Highlight Mode"))
        self.actionHighlight_Mode.setShortcut(_translate("MainWindow", "Ctrl+H"))
        self.actionSave_PDF.setText(_translate("MainWindow", "Save PDF"))
        self.actionSave_PDF.setShortcut(_translate("MainWindow", "Ctrl+S"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
