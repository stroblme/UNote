# ---------------------------------------------------------------
# -- UNote Core File --
#
# Implements core functionality
#
# Author: Melvin Strobl
# ---------------------------------------------------------------

from PyQt5.QtWidgets import QSizePolicy, QFrame, QDialog, QGraphicsView, QGraphicsScene, QApplication, QGraphicsPixmapItem, QGesture, QGraphicsLineItem
from PyQt5.QtCore import Qt, QRectF, QEvent, QThread, pyqtSignal, pyqtSlot, QObject, QPoint
from PyQt5.QtGui import QPixmap

import threading
from interfaces import IregCon, IcsrCtrl
from preferences import Preferences

from pdfEngine import pdfEngine
from imageHelper import imageHelper

from enum import Enum

import subprocess  # for running external cmds
import os
import time

from indexed import IndexedOrderedDict

import fitz

class editModes():
    '''
    This class contains all available edit modes for the current pdf
    '''
    none = 'none'
    mark = 'mark'
    newTextBox = 'newTextBox'
    editTextBox = 'editTextBox'

editMode = editModes.none

class textModes():
    plainText = 'plainText'
    mdText = 'markdownText'

class EventHelper(QObject):
    '''
    This class is intended to extend an existing qt class which does not directly inherit from qobject and therefore does not contain signaling
    '''
    # x, y, pageNumber, currentContent
    requestTextInput = pyqtSignal(int, int, int, str)


class QPdfView(QGraphicsPixmapItem):

    def __init__(self):
        QGraphicsPixmapItem.__init__(self)
        self.blockEdit = False
        self.ongoingEdit = False

        self.eh = EventHelper()

    def setPixMap(self, qImg, pageNumber):
        self.pageNumber = pageNumber

        self.updatePixMap(qImg)

    def updatePixMap(self, qImg):
        self.qImg = qImg

        self.pixImg = QPixmap()
        self.pixImg.convertFromImage(self.qImg)

        self.setPixmap(self.pixImg)

    def setAsOrigin(self):
        self.xOrigin = self.x()
        self.yOrigin = self.y()

        self.wOrigin = self.boundingRect().width()
        self.hOrigin = self.boundingRect().height()

    def setPage(self, page, pageNumber):
        self.page = page
        self.pageNumber = pageNumber

    def reloadQImg(self, zoomFactor):
        mat = fitz.Matrix(zoomFactor, zoomFactor)
        self.pixImg.convertFromImage(self.qImg)

    def startNewTextBox(self, qpos):
        self.ongoingEdit = True
        self.startPos = qpos

    def stopNewTextBox(self, qpos):
        self.endPos = qpos
        self.ongoingEdit = False
        relCorrdinates = self.toPdfCoordinates(qpos)

        self.eh.requestTextInput.emit(relCorrdinates.x(), relCorrdinates.y(), self.pageNumber, "")

    def insertText(self, qpos, content):
        '''
        Inserts a textBox annotion at a specified position
        '''
        if content != "":
            h, w = self.calculateTextRectBounds(content)

            textRect = fitz.Rect(qpos.x(), qpos.y() - h/2, qpos.x() + w, qpos.y() + h/2)

            cyan  = (14/255,125/255,145/255)                                   # some colors
            black = (0,0,0)
            white = (1,1,1)

            border = {"width": 0.4, "dashes": [1]}
            colors = {"stroke": black, "fill": cyan}

            if self.startPos == self.endPos:
                print('no arrow')
            else:
                fStart = fitz.Point(self.startPos.x(), self.startPos.y())
                fEnd = fitz.Point(self.endPos.x(), self.endPos.y())

                lineAnnot = self.page.addPolygonAnnot([fStart, fEnd])
                lineAnnot.setBorder(border)
                lineAnnot.setColors(colors)
                lineAnnot.setLineEnds(fitz.ANNOT_LE_Diamond, fitz.ANNOT_LE_Circle)
                lineAnnot.update()

            textAnnot = self.page.addFreetextAnnot(textRect, content)
            textAnnot.setBorder(border)
            textAnnot.update(fontsize = 14, border_color=cyan, fill_color=white, text_color=black)
            textAnnot.update()




    def editText(self, qpos, content):
        '''
        Searches for a textBox at the current position and updates its content with the provided one
        '''
        for annot in self.page.annots(types=(fitz.PDF_ANNOT_FREE_TEXT, fitz.PDF_ANNOT_TEXT)):
            if self.pointInArea(qpos, annot.rect):
                if content != "":
                    h, w = self.calculateTextRectBounds(content)

                    annot.setRect(fitz.Rect(annot.rect.x0, annot.rect.y0, annot.rect.x0 + w, annot.rect.y0 + h))

                    info = annot.info
                    info["content"] = content
                    info["subject"] = textModes.plainText
                    annot.setInfo(info)
                    annot.update()
                else:
                    self.page.deleteAnnot(annot)

                return

    def textInputReceived(self, x, y, result, content):
        '''
        Called from the graphicView handler when the user has finished editing text in the toolBox textEdit
        '''

        # Check weather the user has edited or inserted a textBox
        if editMode == editModes.newTextBox:
            self.insertText(QPoint(x, y), content)
            self.resetEditMode()
        elif editMode == editModes.editTextBox:
            self.editText(QPoint(x, y), content)
            self.resetEditMode()

    def resetEditMode(self):
        '''
        Simply abstracts the process clearing the current edit mode to prevent a elevation of method access rights to global variables
        '''
        global editMode
        editMode = editModes.none


    def calculateTextRectBounds(self, content):
        '''
        Calculates the optimal rect boundaries for the desired content
        '''

        fontwidth = 8
        defaultHeight = 16
        defaultWidth = 130
        numOfLines = content.count('\n') + 1

        suggestedWidth = defaultWidth
        suggestedHeight = defaultHeight * numOfLines

        # while defaultWidth == suggestedWidth or suggestedHeight > suggestedWidth:

        #     suggestedWidth += suggestedHeight

        #     for line in content.split('\n'):
        #         delta = len(line) * fontwidth - suggestedWidth
        #         if delta > 0:
        #             suggestedHeight += (delta / suggestedWidth) * defaultHeight
        for line in content.split('\n'):
                delta = len(line) * fontwidth - suggestedWidth
                if delta > 0:
                    suggestedHeight += (delta / suggestedWidth) * defaultHeight

        return float(suggestedHeight), float(suggestedWidth)


    def getTextBoxContent(self, qpos):
        for annot in self.page.annots(types=(fitz.PDF_ANNOT_FREE_TEXT, fitz.PDF_ANNOT_TEXT)):
            if self.pointInArea(qpos, annot.rect):
                info = annot.info

                return info["content"]

        return None

    def pointInArea(self, qpos, frect):
        if qpos.x() < frect.x0 or qpos.y() < frect.y0:
            return False

        if qpos.x() > frect.x1 or qpos.y() > frect.y1:
            return False

        return True

    def startMarkText(self, qpos):
        self.ongoingEdit = True
        self.startPos = qpos

    def stopMarkText(self, qpos):
        self.ongoingEdit = False

    def updateMarkText(self, qpos):
        self.endPos = qpos

        yMin = min(self.startPos.y(), self.endPos.y())
        yMax = max(self.startPos.y(), self.endPos.y())

        if abs(yMin - yMax) < 10:
            yMin = yMin - 5
            yMax = yMax + 5

        xMin = min(self.startPos.x(), self.endPos.x())
        xMax = max(self.startPos.x(), self.endPos.x())

        rect = fitz.Rect(xMin, yMin, xMax, yMax)
        self.page.addHighlightAnnot(rect)

    def wheelEvent(self, event):
        '''
        Overrides the default event
        '''
        if not self.ongoingEdit:
            modifiers = QApplication.keyboardModifiers()

            Mmodo = QApplication.mouseButtons()
            if bool(Mmodo == Qt.RightButton) or bool(modifiers == Qt.ControlModifier):
                self.blockEdit = True

        QGraphicsPixmapItem.wheelEvent(self, event)



    def mousePressEvent(self, event):
        '''
        Overrides the default event
        '''
        if self.blockEdit:
            return

        if event.button() == Qt.LeftButton:
            if editMode == editModes.mark:
                self.startMarkText(self.toPdfCoordinates(event.pos()))
            elif editMode == editModes.newTextBox:
                self.startNewTextBox(self.toPdfCoordinates(event.pos()))

    def mouseReleaseEvent(self, event):
        '''
        Overrides the default event
        '''
        global editMode
        self.blockEdit = False

        if event.button() == Qt.LeftButton:
            if editMode == editModes.newTextBox:
                self.stopNewTextBox(self.toPdfCoordinates(event.pos()))
            elif editMode == editModes.mark:
                self.stopMarkText(self.toPdfCoordinates(event.pos()))
        elif event.button() == Qt.RightButton:
            editMode = editModes.editTextBox

            relCorrdinates = self.toPdfCoordinates(event.pos())
            curContent = self.getTextBoxContent(event.pos())
            if curContent:
                self.eh.requestTextInput.emit(relCorrdinates.x(), relCorrdinates.y(), self.pageNumber, curContent)
            else:
                print("Cannot find a text box under that cursor")

    def mouseMoveEvent(self, event):
        '''
        Overrides the default event
        '''
        self.blockEdit = False

        if self.ongoingEdit:
            if editMode == editModes.mark:
                self.updateMarkText(self.toPdfCoordinates(event.pos()))

        QGraphicsPixmapItem.mouseMoveEvent(self, event)

    def toPdfCoordinates(self, qPos):
        '''
        Converts the provided position to relative pdf file coordinates
        '''
        xDif = self.x() - self.xOrigin
        yDif = self.y() - self.yOrigin
        pPos = QPoint(qPos.x() + xDif, qPos.y() + yDif)

        return pPos


class GraphicsViewHandler(QGraphicsView):
    pages = IndexedOrderedDict()
    DEFAULTPAGESPACE = 20
    CONTINOUSVIEW = True

    absZoomFactor = float(1)
    lowResZoomFactor = float(0.1)

    # x, y, pageNumber, currentContent
    requestTextInput = pyqtSignal(int, int, int, str)

    def __init__(self, parent):
        '''
        Creates the graphic view handler instance, which is a main feature of the unot application

        :param parent: Parent editor widget.
        '''
        QGraphicsView.__init__(self, parent)

        self.parent = parent
        self.scaleFactor = 1.0

        self.pdf = pdfEngine()
        self.imageHelper = imageHelper()

        self.setMouseTracking(True)
        self.setTabletTracking(True)
        self.setFrameShape(QFrame.StyledPanel)
        self.setObjectName("graphicsView")

        # self.setDragMode(self.ScrollHandDrag)

        # self.grabGesture(QGesture.gestureType(self))
        # self.resize(parent.size())

    def saveCurrentPdf(self):
        '''
        Just handles saving the pdf
        '''
        self.pdf.savePdf()

    def loadPdfToCurrentView(self, pdfFilePath):
        '''
        Renderes the whole pdf file in the current graphic view instance
        '''
        start_time = time.time()

        self.pdf.openPdf(pdfFilePath)

        self.scene = QGraphicsScene()
        self.setScene(self.scene)

        # Start at the top
        posX = float(0)
        posY = float(0)

        self.qli = QGraphicsLineItem(0,0,0,1)
        self.scene.addItem(self.qli)

        # self.thread = QThread
        # self.moveToThread(self.thread)

        for pIt in range(self.pdf.doc.pageCount):

            if pIt > 2:
                posX, posY = self.loadPdfPageToCurrentView(pIt, posX, posY, self.lowResZoomFactor)
            else:
                if pIt == 2:
                    print('Boosting renderer..')

                # Load each page to a new position in the current view.
                posX, posY = self.loadPdfPageToCurrentView(pIt, posX, posY, self.absZoomFactor)

        print("--- Loaded PDF within %s seconds ---" % (time.time() - start_time))


    def loadPdfPageToCurrentView(self, pageNumber, posX, posY, zoom = None):
        '''
        Creates a qpdfView instance from the desired page and renders it at the provided position with the zoomfactor.
        A lower zoomFactor will dramatically improve speed, as it always correlates to the dpi of the page
        '''
        pdfView = QPdfView()
        pdfView.setPage(self.pdf.getPage(pageNumber), pageNumber)

        self.updatePdf(pdfView, zoom = zoom, pageNumber = pageNumber)


        self.pages[pageNumber] = pdfView

        self.pages[pageNumber].eh.requestTextInput.connect(self.toolBoxTextInputRequestedEvent)

        self.scene.addItem(self.pages[pageNumber])
        self.pages[pageNumber].setPos(posX, posY)

        pdfView.setAsOrigin()

        return posX, posY + pdfView.hOrigin + self.DEFAULTPAGESPACE

    def updateRenderedPages(self):
        '''
        Intended to be called repetitively on every ui change to redraw all visible pdf pages
        '''
        # Get all visible pages
        try:
            renderedItems = self.scene.items(self.mapToScene(self.viewport().geometry()))
        except Exception as e:
            return

        # get the rectable of the current viewport
        rect = self.mapToScene(self.viewport().geometry()).boundingRect()
        # Store those properties for easy access
        viewportHeight = rect.height()
        viewportWidth = rect.width()
        viewportX = rect.x()
        viewportY = rect.y()

        # Iterate all visible items (shouldn't be that much normally)
        for renderedItem in renderedItems:
            # Check if we have a pdf view here (visible could be anything)
            if type(renderedItem) != QPdfView:
                continue

            # There are now a log of switch-case similar things
            # It looks a bit messy as everything has to be done for both, x and y coordinates

            # Initialize clip start coordinates
            clipX = 0
            clipY = 0

            if(renderedItem.xOrigin < viewportX):

                clipX = viewportX - renderedItem.xOrigin

            if(renderedItem.yOrigin < viewportY):

                clipY = viewportY - renderedItem.yOrigin


            if((renderedItem.xOrigin + renderedItem.wOrigin) - (viewportX + viewportWidth) > 0):
                # Start in scope, End not in scope
                if clipX == 0:
                    clipW = (viewportX + viewportWidth) - renderedItem.xOrigin
                # Start not in scope, End not in scope
                else:
                    clipW = viewportWidth

            else:
                # Start in scope, End in scope
                if clipX == 0:
                    clipW = renderedItem.wOrigin
                # Start not in scope, End in scope
                else:
                    clipW = renderedItem.wOrigin - clipX

            if((renderedItem.yOrigin + renderedItem.hOrigin) - (viewportY + viewportHeight) > 0):
                # Start in scope, End not in scope
                if clipY == 0:
                    clipH = (viewportY + viewportHeight) - renderedItem.yOrigin
                # Start not in scope, End not in scope
                else:
                    clipH = viewportHeight

            else:
                # Start in scope, End in scope
                if clipY == 0:
                    clipH = renderedItem.hOrigin
                # Start not in scope, End in scope
                else:
                    clipH = renderedItem.hOrigin - clipY


            clip = QRectF(clipX, clipY, clipW, clipH)

            self.updatePdf(renderedItem, zoom = self.absZoomFactor, clip = clip)

            if clipX != 0:
                rItx = viewportX
            else:
                rItx = renderedItem.xOrigin
            if clipY != 0:
                rIty = viewportY
            else:
                rIty = renderedItem.yOrigin

            renderedItem.setPos(rItx, rIty)


    def toggleTextMode(self):
        '''
        Called from the main ui. Toggles edit mode
        '''
        global editMode

        if editMode == editModes.newTextBox:
            editMode = editModes.none
        else:
            editMode = editModes.newTextBox

    def toggleMarkMode(self):
        '''
        Called from the main ui. Toggles edit mode
        '''
        global editMode

        if editMode == editModes.mark:
            editMode = editModes.none
        else:
            editMode = editModes.mark




    def updatePdf(self, pdf, zoom=absZoomFactor, clip=None, pageNumber = None):
        '''
        Update the provided pdf file at the desired page to render only the zoom and clip
        This methods is used when instantiating the pdf and later, when performance optimzation and zooming is required
        '''
        mat = fitz.Matrix(zoom, zoom)

        fClip = None
        if clip:
            fClip = fitz.Rect(clip.x(), clip.y(), clip.x() + clip.width(), clip.y() + clip.height())

        pixmap = self.pdf.renderPixmap(pdf.page, mat = mat, clip = fClip)

        qImg = self.pdf.getQImage(pixmap)
        qImg.setDevicePixelRatio(zoom)
        qImg = self.imageHelper.applyTheme(qImg)

        if pageNumber:
            pdf.setPixMap(qImg, pageNumber)
        else:
            pdf.updatePixMap(qImg)


    def wheelEvent(self, event):
        '''
        Overrides the default event
        '''
        if not self.scene:
            return

        modifiers = QApplication.keyboardModifiers()

        Mmodo = QApplication.mouseButtons()
        if bool(Mmodo == Qt.RightButton) or bool(modifiers == Qt.ControlModifier):

            zoomInFactor = 1.2
            zoomOutFactor = 1 / zoomInFactor

            # Zoom
            if event.angleDelta().y() > 0:
                relZoomFactor = zoomInFactor
            else:
                relZoomFactor = zoomOutFactor

            self.absZoomFactor = self.absZoomFactor * relZoomFactor
            self.scale(relZoomFactor, relZoomFactor)

        else:
            QGraphicsView.wheelEvent(self, event)


        self.updateRenderedPages()

    def mousePressEvent(self, event):
        '''
        Overrides the default event
        '''
        super(GraphicsViewHandler, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        '''
        Overrides the default event
        '''
        super(GraphicsViewHandler, self).mouseReleaseEvent(event)
        self.updateRenderedPages()

    def mouseMoveEvent(self, event):
        '''
        Overrides the default event
        '''
        self.mousePos = event.localPos()
        super(GraphicsViewHandler, self).mouseMoveEvent(event)
        # self.updateRenderedPages()

    def keyPressEvent(self, event):
        '''
        Overrides the default event
        '''
        self.updateRenderedPages()

        super(GraphicsViewHandler, self).keyPressEvent(event)

    def keyReleaseEvent(self, event):
        '''
        Overrides the default event
        '''
        self.updateRenderedPages()

        super(GraphicsViewHandler, self).keyReleaseEvent(event)

    def gestureEvent(self, event):
        '''
        Overrides the default event
        '''
        print('gesture event received in core.py ')

    @pyqtSlot(int, int, int, bool, str)
    def toolBoxTextInputEvent(self, x, y, pageNumber, result, content):
        '''
        Triggered by the toolBox when user finished text editing
        '''
        # get the desired page which waits for user input
        self.pages[pageNumber].textInputReceived(x, y, result, content)

        # Redraw all, as there are some changes now
        self.updateRenderedPages()

    @pyqtSlot(int, int, int, str)
    def toolBoxTextInputRequestedEvent(self, x, y, pageNumber, currentContent):
        '''
        Triggered by the pdfView when user requests text editing
        '''
        # Call the class intern signal to forward this request to the toolbox
        self.requestTextInput.emit(x, y, pageNumber, currentContent)
