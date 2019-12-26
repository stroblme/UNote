# ---------------------------------------------------------------
# -- CXP Test GUI Helper File --
#
# Utilities for the CXP Test GUI
#
# Author: Melvin Strobl
# ---------------------------------------------------------------
import sys

from PySide2.QtWidgets import QFileDialog, QWidget, QInputDialog
from PySide2.QtCore import QFile, QTextStream, Qt

from PySide2.QtWidgets import QApplication

# sys.path.append('./style')
sys.path.append('./style/BreezeStyleSheets')
import style.BreezeStyleSheets.breeze_resources


class GuiHelper(QWidget):


    def __init__(self):
        super().__init__()

    def openInputDialog(self, title, text):
        qid = QInputDialog(self)

        qid.setAttribute(Qt.WA_TranslucentBackground)

        qid.setWindowFlags(Qt.WindowTitleHint | Qt.FramelessWindowHint)

        resp, ok = qid.getInt(self, title, text)

        return resp, ok

    def openFileNameDialog(self, filter=None, dir = ""):
        '''
        Opens a native File Name Dialog
        Use filter like:
        filter = "All Files (*);;Python Files (*.py)"
        '''

        if not filter:
            filter = "All Files (*)"

        qfd = QFileDialog(self)
        options = qfd.Options()
        # options |= qfd.DontUseNativeDialog
        fileName, _ = qfd.getOpenFileName(self, "Open File", "", filter, options=options)

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

        qfd = QFileDialog(self)
        options = qfd.Options()
        # options |= QFileDialog.DontUseNativeDialog
        fileNames, _ = qfd.getOpenFileNames(self, "Open File", "", filter, options=options)

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

        qfd = QFileDialog(self)
        options = qfd.Options()
        # options |= QFileDialog.DontUseNativeDialog
        fileName, _ = qfd.getSaveFileName(
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
