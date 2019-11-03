# ---------------------------------------------------------------
# -- UNote Receivers File --
#
# Receivers for handling events on the cxptest gui
#
# Author: Melvin Strobl
# ---------------------------------------------------------------

from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal, Qt, QObject, pyqtSlot

import json

from preferences import Preferences
from guiHelper import GuiHelper

class Receivers(QObject):
    '''
    Class for handling all the event calls from the ui
    '''

    SigSendMessageToJS = pyqtSignal(str)

    def __init__(self, uiInst):
        super().__init__()

        self.uiInst = uiInst
        self.guiHelper = GuiHelper()



    def setLogHelperInst(self, logHelper):
        '''
        Used to set the log helper instance after instantiating the unote_receiver obj
        '''
        self.logHelper = logHelper

    def openPreferencesReceiver(self, preferenceInstance):
        '''
        Opens the Preference Window
        '''
        preferenceInstance.run()

        self.uiInst.graphicsView.updateRenderedPages()

    def loadPdf(self):
        '''
        Loads a pdf to the current view
        '''
        pdfFileName = self.guiHelper.openFileNameDialog("PDF File (*.pdf)")

        if pdfFileName == '':
            return

        self.uiInst.graphicsView.loadPdfToCurrentView(pdfFileName)

    def savePdf(self):
        self.uiInst.graphicsView.saveCurrentPdf()

    def pageInsertHere(self):
        self.uiInst.graphicsView.pageInsertHere()

    def pageDeleteActive(self):
        self.uiInst.graphicsView.pageDeleteActive()

    def toggleTextMode(self):
        self.uiInst.graphicsView.toggleTextMode()

        # self.uiInst.actionText_Mode.setChecked(not bool(self.uiInst.actionText_Mode.isChecked()))

    def toggleMarkMode(self):
        self.uiInst.graphicsView.toggleMarkMode()

        # self.uiInst.actionMark_Mode.setChecked(not bool(self.uiInst.actionMark_Mode.isChecked()))


    @pyqtSlot(str)
    def JSSendMessage(self, msg):
        '''
        This method is called each time the webviewer receives a user input.
        msg is a valid json object, containing the following data
        name, id, value
        '''



    def JSReceiveMessage(self, msg):
        '''
        This method provides the interface for sending content in json format to the html viewer.
        A valid json msg contains:
        name, id, value
        '''
        self.SigSendMessageToJS.emit(msg)