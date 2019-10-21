# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'X:\UNote\src\ui\unote_gui.ui',
# licensing of 'X:\UNote\src\ui\unote_gui.ui' applies.
#
# Created: Mon Oct 21 20:47:44 2019
#      by: pyside2-uic  running on PySide2 5.13.1
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

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
        self.graphicsView = QtWidgets.QGraphicsView(self.centralwidget)
        self.graphicsView.setObjectName("graphicsView")
        self.verticalLayout_6.addWidget(self.graphicsView)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout_6.addLayout(self.verticalLayout_2)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1680, 23))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        MainWindow.setMenuBar(self.menubar)
        self.actionLoad_Pattern = QtWidgets.QAction(MainWindow)
        self.actionLoad_Pattern.setObjectName("actionLoad_Pattern")
        self.actionExit = QtWidgets.QAction(MainWindow)
        self.actionExit.setCheckable(False)
        self.actionExit.setObjectName("actionExit")
        self.actionOpen_Register_Map = QtWidgets.QAction(MainWindow)
        self.actionOpen_Register_Map.setObjectName("actionOpen_Register_Map")
        self.actionPreferences = QtWidgets.QAction(MainWindow)
        self.actionPreferences.setObjectName("actionPreferences")
        self.actionCOM = QtWidgets.QAction(MainWindow)
        self.actionCOM.setObjectName("actionCOM")
        self.actionbaud = QtWidgets.QAction(MainWindow)
        self.actionbaud.setObjectName("actionbaud")
        self.dsfa = QtWidgets.QAction(MainWindow)
        self.dsfa.setObjectName("dsfa")
        self.actionport = QtWidgets.QAction(MainWindow)
        self.actionport.setObjectName("actionport")
        self.actionbaud_2 = QtWidgets.QAction(MainWindow)
        self.actionbaud_2.setObjectName("actionbaud_2")
        self.actionDUT_Test = QtWidgets.QAction(MainWindow)
        self.actionDUT_Test.setObjectName("actionDUT_Test")
        self.actionLoad_PDF = QtWidgets.QAction(MainWindow)
        self.actionLoad_PDF.setObjectName("actionLoad_PDF")
        self.menuFile.addAction(self.actionLoad_PDF)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionPreferences)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionExit)
        self.menubar.addAction(self.menuFile.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtWidgets.QApplication.translate("MainWindow", "UNote", None, -1))
        self.menuFile.setTitle(QtWidgets.QApplication.translate("MainWindow", "File", None, -1))
        self.actionLoad_Pattern.setText(QtWidgets.QApplication.translate("MainWindow", "Load Pattern", None, -1))
        self.actionExit.setText(QtWidgets.QApplication.translate("MainWindow", "Exit", None, -1))
        self.actionExit.setShortcut(QtWidgets.QApplication.translate("MainWindow", "Esc", None, -1))
        self.actionOpen_Register_Map.setText(QtWidgets.QApplication.translate("MainWindow", "Open Register Map", None, -1))
        self.actionPreferences.setText(QtWidgets.QApplication.translate("MainWindow", "Preferences", None, -1))
        self.actionPreferences.setShortcut(QtWidgets.QApplication.translate("MainWindow", "P", None, -1))
        self.actionCOM.setText(QtWidgets.QApplication.translate("MainWindow", "port", None, -1))
        self.actionbaud.setText(QtWidgets.QApplication.translate("MainWindow", "baud", None, -1))
        self.dsfa.setText(QtWidgets.QApplication.translate("MainWindow", "Port", None, -1))
        self.actionport.setText(QtWidgets.QApplication.translate("MainWindow", "port", None, -1))
        self.actionbaud_2.setText(QtWidgets.QApplication.translate("MainWindow", "baud", None, -1))
        self.actionDUT_Test.setText(QtWidgets.QApplication.translate("MainWindow", "DUT Test", None, -1))
        self.actionLoad_PDF.setText(QtWidgets.QApplication.translate("MainWindow", "Load PDF", None, -1))
        self.actionLoad_PDF.setShortcut(QtWidgets.QApplication.translate("MainWindow", "O", None, -1))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

