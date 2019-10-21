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

import style.BreezeStyleSheets.breeze_resources

class GuiHelper(QWidget):


    def __init__(self):
        super().__init__()

    def openFileNameDialog(self, filter=None, dir = ""):
        '''
        Opens a native File Name Dialog
        Use filter like:
        filter = "All Files (*);;Python Files (*.py)"
        '''

        if not filter:
            filter = "All Files (*)"

        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(parent = self, caption = "Open File", dir = dir, filter = filter, options = options)

        if fileName:
            print(fileName)

        return fileName

    def openFileNamesDialog(self, filter=None, dir = ""):
        '''
        Opens a native File Names Dialog
        Use filter like:
        filter = "All Files (*);;Python Files (*.py)"
        '''

        if not filter:
            filter = "All Files (*)"

        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileNames, _ = QFileDialog.getOpenFileNames(parent = self, caption = "Open Files", dir = dir, filter = filter, options = options)

        if fileNames:
            print(fileNames)

        return fileNames

    def saveFileDialog(self, filter=None):
        '''
        Opens a native File Save Dialog
        Use filter like:
        filter = "All Files (*);;Python Files (*.py)"
        '''

        if not filter:
            filter = "All Files (*)"

        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(
            self, "Save File", "", filter, options=options)
        if fileName:
            print(fileName)

        return fileName

    def toggle_stylesheet(self, path):
        '''
        Toggle the stylesheet to use the desired path in the Qt resource
        system (prefixed by `:/`) or generically (a path to a file on
        system).

        :path:      A full path to a resource or file on system
        '''

        # get the QApplication instance,  or crash if not set
        app = QApplication.instance()
        if app is None:
            raise RuntimeError("No Qt Application found.")

        file = QFile(path)
        file.open(QFile.ReadOnly | QFile.Text)
        stream = QTextStream(file)
        app.setStyleSheet(stream.readAll())
