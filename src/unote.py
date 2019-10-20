# ---------------------------------------------------------------
# -- UNote Main File --
#
# Main File for running the UNote
#
# Author: Melvin Strobl
# ---------------------------------------------------------------


# ----------------------------------------------------------
# Import region
# ----------------------------------------------------------
from util import readFile, writeFile
from collections import OrderedDict
from core import RegisterMapHandler, ConnectionHandler

from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtGui import QPixmap
from PySide2.QtCore import Signal, QFile, QTextStream, Slot, QObject
from PySide2.QtWidgets import QDialog, QGraphicsView, QGraphicsScene
from PySide2.QtWebEngineWidgets import QWebEnginePage, QWebEngineView
from PySide2.QtWebChannel import QWebChannel


import argparse  # parsing cmdline arguments
import os  # launching external python script
import sys  # exit script, file parsing
import subprocess  # for running external cmds
import atexit

import fitz
from PIL import Image, ImageQt


# app = QApplication(sys.argv)
# file = QFile(":/dark.qss")
# file.open(QFile.ReadOnly | QFile.Text)
# stream = QTextStream(file)
# app.setStyleSheet(stream.readAll())

SCRIPTDIR = os.path.dirname(os.path.realpath(__file__))

# Reload the main ui
subprocess.run('pyside2-uic -x ' + SCRIPTDIR + '\\ui\\preferences_gui.ui -o ' + SCRIPTDIR + '\\ui\\preferences_qt_export.py')

subprocess.run('pyside2-uic -x ' + SCRIPTDIR + '\\ui\\unote_gui.ui -o  ' + SCRIPTDIR + '\\ui\\unote_qt_export.py')

from ui.unote_qt_export import Ui_MainWindow

from unote_receivers import Receivers
from preferences_gui import PreferencesGUI
from preferences import Preferences
from logHelper import LogHelper

class UNote(Ui_MainWindow):
    '''
    Main class for the UNote
    '''

    def __init__(self, debugMode):
        super().__init__()

        self.debugMode = debugMode

        self.initUI()

        t = QtCore.QTimer()
        t.singleShot(0, self.onQApplicationStarted)

        self.qimg = self.renderPdf('X:/UNote/src/test.pdf', 1)
        self.pixImg = QPixmap()
        self.pixImg.convertFromImage(self.qimg)
        self.pixImgItem = QtWidgets.QGraphicsPixmapItem()
        self.pixImgItem.setPixmap(self.pixImg)
        self.scene = QGraphicsScene()
        self.scene.addItem(self.pixImgItem)
        self.ui.graphicsView.setScene(self.scene)
        print('hi')

        self.logHelper = LogHelper(self.ui.plainTextEditConsoleLog)

        self.preferencesGui = PreferencesGUI()

        self.receiversInst = Receivers(self.ui)

        self.connectReceivers()

    def initUI(self):
        self.app = QtWidgets.QApplication(sys.argv)
        self.MainWindow = QtWidgets.QMainWindow()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self.MainWindow)

        self.MainWindow.setWindowIcon(QtGui.QIcon("icon.png"))

    def renderPdf(self, filename, pageNumber):
        doc = fitz.open(filename)
        page = doc.loadPage(pageNumber)
        pix = page.getPixmap()
        mode = "RGBA" if pix.alpha else "RGB"
        img = Image.frombytes(mode, [pix.width, pix.height], pix.samples)
        return ImageQt.ImageQt(img)

    def run(self, args):
        '''
        Starts the UNote
        '''
        self.MainWindow.show()

        result = self.app.exec_()

        self.onQApplicationQuit()

        sys.exit(result)

    def onQApplicationStarted(self):
        '''
        Executed immediately when Application started
        '''
        #Update window sizes
        try:
            self.MainWindow.resize(int(Preferences.data['windowHeight']), int(Preferences.data['windowWidth']))
        except Exception as identifier:
            print("Unable to restore window size: " + str(identifier))

        if self.debugMode:
            self.logHelper.appendLog("GUI is in debug mode. Actual connection handling will be disabled")



    def onQApplicationQuit(self):
        '''
        Executed immediately when Application stops
        '''
        Preferences.updateKeyValue('windowHeight', self.MainWindow.height())
        Preferences.updateKeyValue('windowWidth', self.MainWindow.width())

        self.preferencesGui.storeSettings()

    def connectReceivers(self):
        '''
        Connects all the buttons to the right receivers
        '''
        # Add the exit method
        self.ui.actionExit.triggered.connect(exitMethod)

        # Open Preferences
        self.ui.actionPreferences.triggered.connect(lambda:self.receiversInst.openPreferencesReceiver(self.preferencesGui))

# ----------------------------------------------------------
# User Parameter region
# ----------------------------------------------------------


# ----------------------------------------------------------
# Variable region
# ----------------------------------------------------------


# ----------------------------------------------------------
# Helper Fct for handling input arguments
# ----------------------------------------------------------
def argumentHelper():
    '''
    Just a helper for processing the arguments
    '''

    # Define Help Te
    helpText = 'Register Converter Script'
    # Create ArgumentParser instance
    argparser = argparse.ArgumentParser(description=helpText)

    argparser.add_argument('-u', '--updateUI', action="store_true",
                        help='Index, specifing the sheet number')

    argparser.add_argument('-d', '--debug', action="store_true",
                        help='Debug mode without FPGA Board')

    return argparser.parse_args()


# ----------------------------------------------------------
# Called on script exit
# ----------------------------------------------------------
def exitMethod():
    '''
    Called for exiting the program
    '''

    sys.exit("\n\nExiting UNote\n")


# ----------------------------------------------------------
# Main Entry Point
# ----------------------------------------------------------
def main():
    '''
    Main method handling the flow
    '''

    # -----------------------------------------------------
    # -----------------At Exit Register------------------
    atexit.register(exitMethod)

    # -----------------------------------------------------
    # ---------------Argument processing------------------
    args = None
    try:
        args = argumentHelper()
    except ValueError as e:
        sys.exit("Unable to parse arguments:\n" + str(e))

    UNoteGUI = UNote(args.debug)
    UNoteGUI.run(args)


# Standard python script entry handling
if __name__ == '__main__':
    main()
