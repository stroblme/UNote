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

from util import toBool
from historyHandler import History


class Receivers(QObject):
    '''
    Class for handling all the event calls from the ui
    '''

    SigSendMessageToJS = Signal(str)
    titleUpdate = Signal(str, str)

    def __init__(self, ui):
        super().__init__()

        self.ui = ui
        self.guiHelper = GuiHelper()

        self.ui.splitView = None
        self.ui.graphicsView.changesMade.connect(self.changesMadeReceiver)

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

    def newPdf(self, pdfFileName = None, isDraft=False):
        if not pdfFileName or not isDraft:
            pdfFileName = self.guiHelper.saveFileDialog("PDF File (*.pdf)")

        if pdfFileName and isDraft:
            pdfFileName.open('w')

        # Make sure it's a PDF
        name, ext = os.path.splitext(pdfFileName)
        ext = '.pdf'
        pdfFileName = name + ext

        self.ui.graphicsView.createNewPdf(pdfFileName)

        self.applyWorkspaceDefaults()

        self.updateWindowTitle(pdfFileName, isDraft)


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

        self.updateWindowTitle(pdfFileName)


    def savePdf(self):
        self.ui.graphicsView.saveCurrentPdf()

        self.updateWindowTitle(self.ui.graphicsView.rendererWorker.pdf.filename, False)
        History.resetHistoryChanges()


    def savePdfAs(self, pdfFileName = None):
        if not pdfFileName:
            pdfFileName = self.guiHelper.saveFileDialog("PDF File (*.pdf)")

        if pdfFileName == '':
            return

        self.ui.graphicsView.saveCurrentPdfAs(pdfFileName)

        self.updateWindowTitle(pdfFileName, False)
        History.resetHistoryChanges()

    @Slot(bool)
    def changesMadeReceiver(self, made):
        if made:
            self.updateWindowTitle(self.ui.graphicsView.rendererWorker.pdf.filename, True)
        else:
            self.updateWindowTitle(self.ui.graphicsView.rendererWorker.pdf.filename, False)

    def updateWindowTitle(self, var, isDraft=False):
        if isDraft:
            self.titleUpdate.emit(var, ' *')
        else:
            self.titleUpdate.emit(var, '')

    def pageInsertHere(self):
        self.ui.graphicsView.pageInsertHere()

    def pageDeleteActive(self):
        if self.guiHelper.confirmDialog("Warning", "Are you sure you want to delete the current page?"):
            self.ui.graphicsView.pageDeleteActive()

    def pageGoto(self):
        pageNumber, ok = self.guiHelper.openInputDialog('Goto Page', 'Page Number (<' + str(len(self.ui.graphicsView.pages)) + '): ', int)

        if ok:
            self.ui.graphicsView.pageGoto(pageNumber)

    def pageFind(self):
        findStr, ok = self.guiHelper.openInputDialog('Find', '', str)

        if ok:
            self.ui.graphicsView.pageFind(findStr)

    def applyWorkspaceDefaults(self):
        t = QTimer()


        t.singleShot(10, self.delayedWorkspaceDefaults)

    def delayedWorkspaceDefaults(self):
        if self.ui.graphicsView.rendererWorker.pdf.filename:
            self.ui.graphicsView.zoomToFit()

            pW, pH = self.ui.graphicsView.getPageSize()

            curY = self.ui.floatingToolBox.y()
            # curW = self.ui.floatingToolBox.width()

            self.ui.floatingToolBox.move(pW * self.ui.graphicsView.rendererWorker.absZoomFactor, curY)

    def zoomIn(self):
        self.ui.graphicsView.zoomIn()

        if self.ui.splitView:
            self.ui.splitView.zoomIn()

    def zoomOut(self):
        self.ui.graphicsView.zoomOut()

        if self.ui.splitView:
            self.ui.splitView.zoomOut()

    def zoomToFit(self):
        self.ui.graphicsView.zoomToFit()

        if self.ui.splitView:
            self.ui.splitView.zoomToFit()

    def snippedContainer(self):
        self.ui.splitView = GraphicsViewHandler(self.ui.centralwidget)
        self.ui.splitView.rendererWorker.pdf = self.ui.graphicsView.rendererWorker.pdf
        self.ui.splitView.instructRenderer()
        self.ui.splitView.renderPdfToCurrentView()

        self.ui.snippetContainer.setChildWidget(self.ui.splitView)


        self.ui.floatingToolBox.editModeChange.connect(self.ui.splitView.editModeChangeRequest)
        self.ui.floatingToolBox.suggestUpdate.connect(self.ui.splitView.updateSuggested)

        # Toolboxspecific events
        self.ui.floatingToolBox.textInputFinished.connect(self.ui.splitView.toolBoxTextInputEvent)
        self.ui.splitView.requestTextInput.connect(self.ui.floatingToolBox.handleTextInputRequest)

        t = QTimer()
        t.singleShot(10, self.ui.splitView.zoomToFit)

    @Slot(str)
    def JSSendMessage(self, msg):
        '''
        This method is called each time the webviewer receives a user input.
        msg is a valid json object, containing the following data
        name, id, value
        '''


    def splitView(self):
        if self.ui.actionPageSplitView.isChecked():
            if self.ui.splitView:
                self.ui.gridLayout.itemAtPosition(1,0).widget().setEnabled(True)
                self.ui.gridLayout.itemAtPosition(1,0).widget().setVisible(True)

                t = QTimer()
                t.singleShot(10, self.ui.splitView.zoomToFit)
                t.singleShot(15, self.syncPages)
                t.singleShot(20, self.ui.graphicsView.updateRenderedPages)

            else:
                self.ui.splitView = GraphicsViewHandler(self.ui.centralwidget)
                self.ui.splitView.rendererWorker.pdf = self.ui.graphicsView.rendererWorker.pdf
                self.ui.splitView.renderPdfToCurrentView()

                self.ui.seperator = QHLine()

                # self.ui.gridLayout.addWidget(self.ui.seperator, 1, 0)
                self.ui.gridLayout.addWidget(self.ui.splitView, 1, 0)

                self.ui.floatingToolBox.editModeChange.connect(self.ui.splitView.editModeChangeRequest)
                self.ui.floatingToolBox.suggestUpdate.connect(self.ui.splitView.updateSuggested)

                # Toolboxspecific events
                self.ui.floatingToolBox.textInputFinished.connect(self.ui.splitView.toolBoxTextInputEvent)
                self.ui.splitView.requestTextInput.connect(self.ui.floatingToolBox.handleTextInputRequest)

                t = QTimer()
                t.singleShot(10, self.ui.splitView.zoomToFit)
                t.singleShot(15, self.syncPages)
                t.singleShot(20, self.ui.graphicsView.updateRenderedPages)
        else:
            self.ui.gridLayout.itemAtPosition(1,0).widget().setEnabled(False)
            self.ui.gridLayout.itemAtPosition(1,0).widget().setVisible(False)
            # self.ui.gridLayout.removeWidget(self.ui.gridLayout.itemAtPosition(1,0).widget())

    def syncPages(self):
        curNum = self.ui.graphicsView.getCurrentPageNumber()

        self.ui.splitView.pageGoto(curNum+1)

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