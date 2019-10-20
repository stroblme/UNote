# ---------------------------------------------------------------
# -- CXP Test GUI Helper File --
#
# Utilities for the CXP Test GUI
#
# Author: Melvin Strobl
# ---------------------------------------------------------------

from PySide2 import QtWidgets, QtCore
from PySide2.QtWidgets import QFileDialog, QWidget
from PySide2.QtCore import QSettings, QFile, QTextStream

from PySide2.QtWidgets import QApplication


class LogHelper(QWidget):


    def __init__(self, logTextBox, parent = None):
        super().__init__()

        self.logTextBox = logTextBox

    def appendLog(self, text):
        '''
        Appends a text to the log window
        '''
        entry =  "\n > " + str(text) + self.logTextBox.toPlainText()
        self.logTextBox.setPlainText(entry)


    def clearLog(self):
        '''
        Clears the log window
        '''
        pass

    def saveLog(self):
        '''
        Saves the log window
        '''
        pass
