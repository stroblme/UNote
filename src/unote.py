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
import time

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import pyqtSignal, QFile, QTextStream, pyqtSlot, QObject
from PyQt5.QtWidgets import QDialog, QGraphicsView, QGraphicsScene, QWidget


import argparse  # parsing cmdline arguments
import os  # launching external python script
import sys  # exit script, file parsing
import subprocess  # for running external cmds
import atexit


# app = QApplication(sys.argv)
# file = QFile(":/dark.qss")
# file.open(QFile.ReadOnly | QFile.Text)
# stream = QTextStream(file)
# app.setStyleSheet(stream.readAll())

SCRIPTDIR = os.path.dirname(os.path.realpath(__file__))


from ui.unote_qt_export import Ui_MainWindow

from unote_receivers import Receivers
from preferences_gui import PreferencesGUI
from preferences import Preferences
from core import GraphicsViewHandler
from toolbox import ToolBoxWidget

class UNote(Ui_MainWindow):
    '''
    Main class for the UNote
    '''

    def __init__(self, pdfLoad):
        super().__init__()


        self.initUI()

        t = QtCore.QTimer()
        t.singleShot(0, self.onQApplicationStarted)



        self.preferencesGui = PreferencesGUI()

        self.receiversInst = Receivers(self.ui)

        self.connectReceivers()

        if pdfLoad:
            self.ui.graphicsView.loadPdfToCurrentView(os.path.abspath(pdfLoad))


    def initUI(self):
        self.app = QtWidgets.QApplication(sys.argv)
        self.MainWindow = QtWidgets.QMainWindow()
        # self.MainWindow.setWindowFlags(QtCore.Qt.WindowTitleHint | QtCore.Qt.FramelessWindowHint)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self.MainWindow)

        self.MainWindow.setWindowIcon(QtGui.QIcon("icon.png"))

        self.ui.graphicsView = GraphicsViewHandler(self.ui.centralwidget)
        self.ui.gridLayout.addWidget(self.ui.graphicsView, 0, 0, 1, 1)

        self.ui.floatingToolBox = ToolBoxWidget(self.MainWindow)
        self.ui.floatingToolBox.setWindowFlags(QtCore.Qt.WindowTitleHint | QtCore.Qt.FramelessWindowHint)
        self.ui.floatingToolBox.setObjectName("floatingToolBox")
        self.ui.floatingToolBox.setGeometry(QtCore.QRect(200, self.MainWindow.height()-200, 200, 200))
        self.ui.floatingToolBox.show()



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
            self.MainWindow.setGeometry(int(Preferences.data['windowXPos']), int(Preferences.data['windowYPos']), int(Preferences.data['windowWidth']), int(Preferences.data['windowHeight']))
        except Exception as identifier:
            print("Unable to restore window size: " + str(identifier))

            try:
                self.MainWindow.setGeometry(0,0, 1920,1080)
            except:
                print("Even unable to restore default window size. Is there even a monitor attached?")







    def onQApplicationQuit(self):
        '''
        Executed immediately when Application stops
        '''
        Preferences.updateKeyValue('windowHeight', self.MainWindow.height())
        Preferences.updateKeyValue('windowWidth', self.MainWindow.width())
        Preferences.updateKeyValue('windowXPos', self.MainWindow.x())
        Preferences.updateKeyValue('windowYPos', self.MainWindow.y())

        self.preferencesGui.storeSettings()

    def connectReceivers(self):
        '''
        Connects all the buttons to the right receivers
        '''
        # Add the exit method
        self.ui.actionExit.triggered.connect(exitMethod)

        # Open Preferences
        self.ui.actionPreferences.triggered.connect(lambda:self.receiversInst.openPreferencesReceiver(self.preferencesGui))

        # Load PDF File
        self.ui.actionLoad_PDF.triggered.connect(lambda:self.receiversInst.loadPdf())

        self.ui.actionText_Mode.triggered.connect(lambda:self.receiversInst.toggleTextMode())
        self.ui.actionHighlight_Mode.triggered.connect(lambda:self.receiversInst.toggleHighlightMode())

        self.ui.actionSave_PDF.triggered.connect(lambda:self.receiversInst.savePdf())

        self.ui.floatingToolBox.textInputFinished.connect(self.ui.graphicsView.toolBoxTextInputEvent)

        self.ui.graphicsView.requestTextInput.connect(self.ui.floatingToolBox.handleTextInputRequest)
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

    argparser.add_argument('-p', '--pdf',
                        help='Load pdf')

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

    if args.updateUI:
        subprocess.run('py -3 -m PyQt5.uic.pyuic .\\ui\\unote_gui.ui -o .\\ui\\unote_qt_export.py -x')
        subprocess.run('py -3 -m PyQt5.uic.pyuic .\\ui\\preferences_gui.ui -o .\\ui\\preferences_qt_export.py -x')


    from ui.unote_qt_export import Ui_MainWindow

    UNoteGUI = UNote(args.pdf)
    UNoteGUI.run(args)


# Standard python script entry handling
if __name__ == '__main__':
    main()
