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
from fbs_runtime.application_context.PySide2 import ApplicationContext

import argparse  # parsing cmdline arguments
import os  # launching external python script
import sys  # exit script, file parsing
import atexit
from pathlib import Path

from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QMainWindow, QWidget
from PySide2.QtCore import QTimer, Qt, QRect, QObject, Signal, Slot

SCRIPTDIR = os.path.dirname(os.path.realpath(__file__))

from core import GraphicsViewHandler
from unote_receivers import Receivers
from preferences import Preferences
from toolbox import ToolBoxWidget
from preferences_gui import PreferencesGUI
from widgetContainer import TContainer

from unote_qt_export import Ui_MainWindow

print('Dependencies loaded')

class App(QObject):
    appctxt = ApplicationContext()

    ICONPATH = appctxt.get_resource('icon.png')
    CURVERSION = "2020.01"

    DONATEURL   = "https://www.paypal.me/vinstrobl/coffee"
    UPDATEURL   = "http://unote.stroblme.tech/archives/UNote.zip"
    ABOUTURL    = "https://unote.stroblme.tech/"

    TOOLBOXWIDTH = 200
    TOOLBOXHEIGHT = 200
    TOOLBOXSTARTX = 400
    TOOLBOXSTARTY = 500

    # MAINWINDOWSTARTX = 0
    # MAINWINDOWSTARTY = 0
    # MAINWINDOWWIDTH = 1920
    # MAINWINDOWHEIGHT = 1080
class MainWindow(QMainWindow):
    resizeSignal = Signal()

    def resizeEvent(self, event):
        self.resizeSignal.emit()
        return QMainWindow.resizeEvent(self, event)

class UNote(App):
    '''
    Main class for the UNote
    '''

    def __init__(self, args):
        super().__init__()

        self.initUI()

        t = QTimer()
        t.singleShot(0, self.onQApplicationStarted)



        self.preferencesGui = PreferencesGUI(self.appctxt, self.PreferenceWindow)

        self.receiversInst = Receivers(self.ui)

        self.connectReceivers()

        self.ui.floatingToolBox.restoreDefaults()

        if args != '':
            if os.path.isfile(args):
                self.receiversInst.loadPdf(os.path.abspath(args))

            elif args:
                self.receiversInst.newPdf(os.path.abspath(args))



    def initUI(self):
        '''
        Initialize mandatory ui components
        '''
        # Create an application context
        # self.app = QtWidgets.QApplication(sys.argv)

        self.MainWindow = MainWindow()

        self.ui = Ui_MainWindow()

        # Load the ui definitions generated by qt designer
        self.ui.setupUi(self.MainWindow)

        # Load the icon
        self.MainWindow.setWindowIcon(QIcon(self.ICONPATH))

        # Get the preferences window ready
        self.PreferenceWindow = QWidget(self.MainWindow)
        self.PreferenceWindow.move(self.MainWindow.width()/2 - 500, self.MainWindow.height()/2 - 250)

        # Initialize graphicviewhandler. This is a core component of unote
        self.ui.graphicsView = GraphicsViewHandler(self.ui.centralwidget)
        # Simply use the whole window
        self.ui.gridLayout.addWidget(self.ui.graphicsView, 0, 0)

        # Initialize a floating toolboxwidget. This is used for storing tools and editing texts
        self.ui.floatingToolBox = ToolBoxWidget(self.MainWindow)
        self.ui.floatingToolBox.setWindowFlags(Qt.WindowTitleHint | Qt.FramelessWindowHint)
        self.ui.floatingToolBox.setObjectName("floatingToolBox")
        self.ui.floatingToolBox.setGeometry(QRect(self.MainWindow.width() - self.TOOLBOXWIDTH,self.TOOLBOXHEIGHT, self.TOOLBOXWIDTH, self.TOOLBOXHEIGHT))
        self.ui.floatingToolBox.show()
        # self.ui.floatingToolBox.setStyleSheet("background-color:black")

        from PySide2.QtCore import QPoint

        self.ui.snippetContainer = TContainer(self.MainWindow, QPoint(100,100))

        self.MainWindow.resizeSignal.connect(self.onAppResize)

    @Slot(str)
    def updateWindowTitle(self, var):
        if str(var) != "":
            # Override window title
            self.MainWindow.setWindowTitle("UNote - " + Path(str(var)).stem)

        else:
            # Reset the title
            self.MainWindow.setWindowTitle("UNote")

    def run(self):
        '''
        Starts the UNote
        '''
        self.MainWindow.show()

        result = self.appctxt.app.exec_()

        self.onQApplicationQuit()

        sys.exit(result)

    def onQApplicationStarted(self):
        '''
        Executed immediately when Application started
        '''
        #Restore window pos
        try:
            self.MainWindow.restoreGeometry(bytearray(Preferences.data['geometry'],"utf-8"))
            self.MainWindow.restoreState(bytearray(Preferences.data['state'],"utf-8"))
        except Exception as identifier:
            print("Unable to restore window size: " + str(identifier))

        # Initialize auto saving
        # self.autoSaveReceiver()
    def onAppResize(self):
        self.PreferenceWindow.move(self.MainWindow.width()/2 - 500, self.MainWindow.height()/2 - 250)
        self.ui.floatingToolBox.move(self.MainWindow.width() - self.TOOLBOXWIDTH, self.TOOLBOXHEIGHT)

        self.receiversInst.applyWorkspaceDefaults()



    def onQApplicationQuit(self):
        '''
        Executed immediately when Application stops
        '''
        Preferences.updateKeyValue('geometry', self.MainWindow.saveGeometry())
        Preferences.updateKeyValue('state', self.MainWindow.saveState())

        self.preferencesGui.storeSettings()


    def connectReceivers(self):
        '''
        Connects all the buttons to the right receivers
        '''
        # Add the exit method
        self.ui.actionExit.triggered.connect(self.appctxt.app.quit)

        # Open Preferences
        self.ui.actionPreferences.triggered.connect(lambda: self.receiversInst.openPreferencesReceiver(self.preferencesGui))

        # Create new PDF file
        self.ui.actionNew_PDF.triggered.connect(lambda: self.receiversInst.newPdf())

        # Load PDF File
        self.ui.actionLoad_PDF.triggered.connect(lambda: self.receiversInst.loadPdf())

        # Save PDF
        self.ui.actionSave_PDF.triggered.connect(lambda: self.receiversInst.savePdf())

        # Save PDF as
        self.ui.actionSave_PDF_as.triggered.connect(lambda: self.receiversInst.savePdfAs())

        # Insert PDF Page
        self.ui.actionPageInsertHere.triggered.connect(lambda: self.receiversInst.pageInsertHere())

        # Remove PDF Paage
        self.ui.actionPageDeleteActive.triggered.connect(lambda: self.receiversInst.pageDeleteActive())

        # Goto Page
        self.ui.actionPageGoto.triggered.connect(lambda: self.receiversInst.pageGoto())

        # Zoom In
        self.ui.actionZoomIn.triggered.connect(lambda: self.receiversInst.zoomIn())

        # Zoom Out
        self.ui.actionZoomOut.triggered.connect(lambda: self.receiversInst.zoomOut())

        # Zoom To Fit
        self.ui.actionZoomToFit.triggered.connect(lambda: self.receiversInst.zoomToFit())

        # Split View
        self.ui.actionPageSplitView.triggered.connect(lambda: self.receiversInst.splitView())

        # Toolbox Edit modes available
        self.ui.floatingToolBox.editModeChange.connect(self.ui.graphicsView.editModeChangeRequest)

        # Suggest update signal
        self.ui.floatingToolBox.suggestUpdate.connect(self.ui.graphicsView.updateSuggested)

        # Toolboxspecific events
        self.ui.floatingToolBox.textInputFinished.connect(self.ui.graphicsView.toolBoxTextInputEvent)
        self.ui.graphicsView.requestTextInput.connect(self.ui.floatingToolBox.handleTextInputRequest)

        self.ui.actionHelpDonate.triggered.connect(lambda: self.receiversInst.donateReceiver(self.DONATEURL))

        self.ui.actionHelpCheck_for_Updates.triggered.connect(lambda: self.receiversInst.checkForUpdatesReceiver(self.UPDATEURL))

        self.ui.actionHelpAbout.triggered.connect(lambda: self.receiversInst.aboutReceiver(self.ABOUTURL))

        self.receiversInst.titleUpdate.connect(self.updateWindowTitle)
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

    argparser.add_argument('open', metavar='o',
                        help='Open existing pdf from path')
    argparser.add_argument('-n', '--new',
                        help='Create new pdf at path')

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
    # args = None
    # try:
    #     args = argumentHelper()
    # except ValueError as e:
    #     sys.exit("Unable to parse arguments:\n" + str(e))
    try:
        args = sys.argv[1]
    except IndexError as identifier:
        args = ''

    UNoteGUI = UNote(args)
    UNoteGUI.run()


# Standard python script entry handling
if __name__ == '__main__':
    main()
