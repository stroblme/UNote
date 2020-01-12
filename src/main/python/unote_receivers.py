# ---------------------------------------------------------------
# -- UNote Receivers File --
#
# Receivers for handling events on the cxptest gui
#
# Author: Melvin Strobl
# ---------------------------------------------------------------
import os
import webbrowser

from PySide2.QtCore import Signal, QObject, Slot, QTimer

from preferences import Preferences
from guiHelper import GuiHelper, QHLine

from core import GraphicsViewHandler



class Receivers(QObject):
    '''
    Class for handling all the event calls from the ui
    '''

    SigSendMessageToJS = Signal(str)

    def __init__(self, ui):
        super().__init__()

        self.ui = ui
        self.guiHelper = GuiHelper()

        # self.backgroundEffect = QGraphicsDropShadowEffect(self)
        # self.backgroundEffect.setColor(QColor(0,0,0))
        # self.backgroundEffect.setEnabled(False)


        # self.ui.centralwidget.setGraphicsEffect(self.backgroundEffect)
        # self.ui.centralwidget.setGraphicsEffect(self.backgroundEffect)




    def setLogHelperInst(self, logHelper):
        '''
        Used to set the log helper instance after instantiating the unote_receiver obj
        '''
        self.logHelper = logHelper

    def openPreferencesReceiver(self, preferenceInstance):
        '''
        Opens the Preference Window
        '''
        # self.backgroundEffect.setEnabled(True)

        preferenceInstance.run()

        # self.backgroundEffect.setEnabled(False)

        self.ui.graphicsView.updateRenderedPages()

    def newPdf(self, pdfFileName = None):
        if not pdfFileName:
            pdfFileName = self.guiHelper.saveFileDialog("PDF File (*.pdf)")

        if pdfFileName == '':
            return

        name, ext = os.path.splitext(pdfFileName)

        ext = '.pdf'

        pdfFileName = name + ext

        self.ui.graphicsView.createNewPdf(pdfFileName)

        self.applyWorkspaceDefaults()

    def loadPdf(self, pdfFileName = None):
        '''
        Loads a pdf to the current view
        '''
        if not pdfFileName:
            pdfFileName = self.guiHelper.openFileNameDialog("PDF File (*.pdf)")

        if pdfFileName == '':
            return

        self.ui.graphicsView.loadPdfToCurrentView(pdfFileName)

        self.applyWorkspaceDefaults()

    def savePdf(self):
        self.ui.graphicsView.saveCurrentPdf()

    def savePdfAs(self, pdfFileName = None):
        if not pdfFileName:
            pdfFileName = self.guiHelper.saveFileDialog("PDF File (*.pdf)")

        if pdfFileName == '':
            return

        self.ui.graphicsView.saveCurrentPdfAs(pdfFileName)

    def pageInsertHere(self):
        self.ui.graphicsView.pageInsertHere()

    def pageDeleteActive(self):
        if self.guiHelper.confirmDialog("Warning", "Are you sure you want to delete the current page?"):
            self.ui.graphicsView.pageDeleteActive()

    def pageGoto(self):
        pageNumber, ok = self.guiHelper.openInputDialog('Goto Page', 'Page Number (<' + str(len(self.ui.graphicsView.pages)) + '): ')

        if ok:
            self.ui.graphicsView.pageGoto(pageNumber)

    def applyWorkspaceDefaults(self):
        t = QTimer()


        t.singleShot(10, self.delayedWorkspaceDefaults)

    def delayedWorkspaceDefaults(self):
        if self.ui.graphicsView.pdf.filename:
            self.ui.graphicsView.zoomToFit()

            pW, pH = self.ui.graphicsView.getPageSize()

            curY = self.ui.floatingToolBox.y()
            # curW = self.ui.floatingToolBox.width()

            self.ui.floatingToolBox.move(pW * self.ui.graphicsView.absZoomFactor, curY)

    def zoomIn(self):
        self.ui.graphicsView.zoomIn()

    def zoomOut(self):
        self.ui.graphicsView.zoomOut()

    def zoomToFit(self):
        self.ui.graphicsView.zoomToFit()

    def splitView(self):
        self.ui.splitView = GraphicsViewHandler(self.ui.centralwidget)
        self.ui.splitView.pdf = self.ui.graphicsView.pdf
        self.ui.splitView.renderPdfToCurrentView()

        self.ui.seperator = QHLine()

        self.ui.gridLayout.addWidget(self.ui.seperator, 1, 0)

        self.ui.gridLayout.addWidget(self.ui.splitView, 2, 0)

        self.ui.floatingToolBox.editModeChange.connect(self.ui.splitView.editModeChangeRequest)
        self.ui.floatingToolBox.suggestUpdate.connect(self.ui.splitView.updateSuggested)

        # Toolboxspecific events
        self.ui.floatingToolBox.textInputFinished.connect(self.ui.splitView.toolBoxTextInputEvent)
        self.ui.splitView.requestTextInput.connect(self.ui.floatingToolBox.handleTextInputRequest)

        t = QTimer()
        t.singleShot(10, self.ui.splitView.zoomToFit)

    def toggleTextMode(self):
        self.ui.graphicsView.toggleTextMode()

        # self.ui.actionText_Mode.setChecked(not bool(self.ui.actionText_Mode.isChecked()))

    def toggleMarkMode(self):
        self.ui.graphicsView.toggleMarkMode()

        # self.ui.actionMark_Mode.setChecked(not bool(self.ui.actionMark_Mode.isChecked()))


    @Slot(str)
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

    def aboutReceiver(self, url):
        webbrowser.open(url)

    def checkForUpdatesReceiver(self, url):
        webbrowser.open(url)

    def donateReceiver(self, url):
        #Buy me a coffee <3
        webbrowser.open(url)