# ---------------------------------------------------------------
# -- UNote Core File --
#
# Implements core functionality
#
# Author: Melvin Strobl
# ---------------------------------------------------------------

from PyQt5.QtWidgets import QSizePolicy, QFrame, QDialog, QGraphicsView, QGraphicsScene, QApplication, QGraphicsPixmapItem, QGesture, QGraphicsLineItem, QGraphicsEllipseItem, QGesture
from PyQt5.QtCore import Qt, QRectF, QEvent, QThread, pyqtSignal, pyqtSlot, QObject, QPoint
from PyQt5.QtGui import QPixmap, QBrush, QColor, QImage, QPaintEvent, QFocusEvent, QHoverEvent, QTouchEvent
from PyQt5.QtWebEngineWidgets import QWebEngineView
import threading
from preferences import Preferences

from pdfEngine import pdfEngine
from imageHelper import imageHelper
from markdownHelper import markdownHelper

from enum import Enum

import subprocess  # for running external cmds
import os
import sys
import time

from indexed import IndexedOrderedDict

import fitz

from editHelper import editModes
from filters import Kalman, Savgol, FormEstimator

sys.path.append('./style')
from styledef import rgb, norm_rgb, pdf_annots

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
    addIndicatorPoint = pyqtSignal(int, int)
    deleteLastIndicatorPoint = pyqtSignal()


class QPdfView(QGraphicsPixmapItem):
    startPos = 0
    endPos = 0
    ongoingEdit = False
    blockEdit = False

    def __init__(self):
        QGraphicsPixmapItem.__init__(self)
        self.blockEdit = False
        self.ongoingEdit = False

        self.eh = EventHelper()

        self.savgol = Savgol()
        self.formEstimator = FormEstimator()

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

    def qPointToFPoint(self, qPoint):
        return fitz.Point(qPoint.x(), qPoint.y())

    def qPointToFloatParirs(self, qPoint):
        p = (float(qPoint.x()), float(qPoint.y()))
        return p

    def fPointToQPoint(self, fPoint):
        return QPoint(fPoint.x, fPoint.y)

    #-----------------------------------------------------------------------
    # Markdown Box
    #-----------------------------------------------------------------------

    def startNewMarkdownBox(self, qpos):
        self.ongoingEdit = True
        self.startPos = qpos

    def stopNewMarkdownBox(self, qpos):
        self.ongoingEdit = False
        self.endPos = qpos

        self.eh.requestTextInput.emit(self.endPos.x(), self.endPos.y(), self.pageNumber, "")

    def insertMarkdown(self, qpos, content):
        self.preview = QWebEngineView()

        self.mdHelper = markdownHelper()

        self.ppage = self.mdHelper.loadGetMarkdownPage(content)

        self.preview.setPage(self.ppage)


    #-----------------------------------------------------------------------
    # Text Box
    #-----------------------------------------------------------------------

    def startNewTextBox(self, qpos):
        self.ongoingEdit = True
        self.startPos = qpos

    def stopNewTextBox(self, qpos):
        self.ongoingEdit = False
        self.endPos = qpos

        self.eh.requestTextInput.emit(self.endPos.x(), self.endPos.y(), self.pageNumber, "")

    def insertText(self, qpos, content):
        '''
        Inserts a textBox annotion at a specified position
        '''
        if content != "":
            h, w = self.calculateTextRectBounds(content)

            textRect = fitz.Rect(qpos.x(), qpos.y() - h/2, qpos.x() + w, qpos.y() + h/2)

            textRect = self.calculateTextRectPos(textRect)

            cyan  = norm_rgb.main
            black = norm_rgb.black
            white = norm_rgb.white

            borderText = {"width": pdf_annots.lineWidth, "dashes": [pdf_annots.dashLevel]}
            colors = {"stroke": black, "fill": cyan}

            try:
                textSize = pdf_annots.defaultTextSize * (int(Preferences.data['textSize'])/100)
            except ValueError:
                textSize = pdf_annots.defaultTextSize

            textAnnot = self.page.addFreetextAnnot(textRect, content)
            textAnnot.setBorder(borderText)
            textAnnot.update(fontsize = textSize, border_color=cyan, fill_color=white, text_color=black)

            if self.startPos != self.endPos:
                fStart, fEnd = self.recalculateLinePoints(textRect, self.startPos)

                lineXref = self.insertLine(fStart, fEnd, "")

                textAnnotInfo = textAnnot.info
                textAnnotInfo["subject"] = str(lineXref)
                textAnnot.setInfo(textAnnotInfo)

                self.eh.deleteLastIndicatorPoint.emit()

            self.eh.deleteLastIndicatorPoint.emit()

            textAnnot.update()
        else:
            # Only when there is a line
            if self.startPos != self.endPos:
                self.eh.deleteLastIndicatorPoint.emit()

    def insertLine(self, fStart, fEnd, subj):
        cyan  = norm_rgb.main
        borderLine = {"width": pdf_annots.borderWidth}

        lineAnnot = self.page.addLineAnnot(fStart, fEnd)

        lineAnnotInfo = lineAnnot.info
        lineAnnotInfo["subject"] = subj
        lineAnnot.setInfo(lineAnnotInfo)

        lineAnnot.setBorder(borderLine)
        lineAnnot.setLineEnds(fitz.ANNOT_LE_Circle, fitz.ANNOT_LE_Circle)
        lineAnnot.update(border_color=cyan, fill_color=cyan)
        lineAnnot.update()

        return lineAnnot.xref

    def recalculateLinePoints(self, textBoxRect, startPoint):
        '''
        Returns the start and end points of a line connected to the provided rect so, that the line won't intersect the rect
        '''
        if startPoint.x() > textBoxRect.x1:
            fEndX = textBoxRect.x1
        elif startPoint.x() < textBoxRect.x0:
            fEndX = textBoxRect.x0
        else:
            fEndX = textBoxRect.x0 + (textBoxRect.x1 - textBoxRect.x0) / 2

        if startPoint.y() > textBoxRect.y1:
            fEndY = textBoxRect.y1
        elif startPoint.y() < textBoxRect.y0:
            fEndY = textBoxRect.y0
        else:
            fEndY = textBoxRect.y0 + (textBoxRect.y1 - textBoxRect.y0) / 2

        fStart = fitz.Point(startPoint.x(), startPoint.y())
        fEnd = fitz.Point(fEndX, fEndY)

        return fStart, fEnd

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
                    annot.setInfo(info)
                    annot.update()
                else:
                    self.deleteAnnot(annot)

                return

    def textInputReceived(self, x, y, result, content):
        '''
        Called from the graphicView handler when the user has finished editing text in the toolBox textEdit
        '''

        # Check weather the user has edited or inserted a textBox
        if editMode == editModes.newTextBox:
            self.insertText(QPoint(x, y), content)
            self.resetEditMode()
            self.eh.deleteLastIndicatorPoint.emit()

        elif editMode == editModes.editTextBox:
            self.editText(QPoint(x, y), content)
            self.resetEditMode()
            self.removeVisualCorners()

        elif editMode == editModes.markdown:
            self.insertMarkdown(QPoint(x, y), content)
            self.resetEditMode()
            self.eh.deleteLastIndicatorPoint.emit()

    def deleteAnnot(self, annot):
        '''
        Deletes the desired annot and the corresponding line if one is found
        '''
        # Check if there is a corresponding line annot
        corrAnnot = self.getCorrespondingAnnot(annot)
        if corrAnnot:
            self.page.deleteAnnot(corrAnnot)

        self.page.deleteAnnot(annot)

    def getCorrespondingAnnot(self, annot):
        info = annot.info
        lineXRef = None
        # Try to get the corresponding xref for the line
        try:
            lineXRef = int(info["subject"])
        except ValueError as e:
            # This can and should happen, when the obj has no child
            return None
        except Exception as e:
            print('While deleting Annot\t' + str(e))
            return None

        if lineXRef:
            lineAnnot = self.getAnnotWithXref(lineXRef)
            return lineAnnot

        return None

    def startMoveObject(self, qpos, annot):
        self.ongoingEdit = True
        self.startPos = qpos
        self.currAnnot = annot

    def stopMoveObject(self, qpos):
        self.ongoingEdit = False
        self.endPos = qpos
        self.moveAnnotByDelta(self.startPos, self.endPos, self.currAnnot)

    def moveAnnotByDelta(self, startQPos, endQPos, annot):
        '''
        Moves an annot by the delta of the two provided positions.
        '''
        dx = endQPos.x() - startQPos.x()
        dy = endQPos.y() - startQPos.y()

        if dx == 0 and dy == 0:
            return

        # Calculate new text
        nRect = fitz.Rect(annot.rect.x0 + dx, annot.rect.y0 + dy, annot.rect.x1 + dx, annot.rect.y1 + dy)

        # Check if destination is outside page. Correct if so
        nRect = self.calculateTextRectPos(nRect)

        annot.setRect(nRect)
        annot.update()

        # Now check if there is a line which needs to be redrawn
        corrAnnot = self.getCorrespondingAnnot(annot)
        if corrAnnot:
            lineInfo = corrAnnot.info
            lineSubj = lineInfo["subject"]

            corrVertices = corrAnnot.vertices
            startPos = corrVertices[0]
            endPos = corrVertices[1]

            fStart, fEnd = self.recalculateLinePoints(annot.rect, QPoint(*startPos))

            self.deleteAnnot(corrAnnot)
            newXRef = self.insertLine(fStart, fEnd, lineSubj)

            textInfo = annot.info
            textInfo["subject"] = str(newXRef)
            annot.setInfo(textInfo)
            annot.update()

    #-----------------------------------------------------------------------
    # Marker
    #-----------------------------------------------------------------------

    def startMarkText(self, qpos):
        self.ongoingEdit = True
        self.startPos = qpos

    def stopMarkText(self, qpos):
        self.ongoingEdit = False
        self.endPos = qpos

        self.updateMarkText()

    def updateMarkText(self):
        '''
        Called updates the currently ongoing marking to match the latest, provided position
        '''
        yMin = min(self.startPos.y(), self.endPos.y())
        yMax = max(self.startPos.y(), self.endPos.y())

        try:
            minWidth = pdf_annots.defaultMarkerSize * (int(Preferences.data['markerSize'])/100)
        except ValueError:
            minWidth = pdf_annots.defaultMarkerSize

        # Ensure at least a width of 10
        if abs(yMin - yMax) < minWidth:
            yMin = yMin - minWidth/2
            yMax = yMax + minWidth/2

        xMin = min(self.startPos.x(), self.endPos.x())
        xMax = max(self.startPos.x(), self.endPos.x())

        rect = fitz.Rect(xMin, yMin, xMax, yMax)
        self.page.addHighlightAnnot(rect)

    #-----------------------------------------------------------------------
    # Eraser
    #-----------------------------------------------------------------------


    def startEraser(self, qpos):
        self.ongoingEdit = True
        self.startPos = qpos

        self.eraserPoints = []

    def stopEraser(self, qpos):
        self.ongoingEdit = False

        self.applyEraser()

    def updateEraserPoints(self, qpos):
        '''
        Called updates the currently ongoing marking to match the latest, provided position
        '''
        self.eraserPoints.append(qpos)

    def applyEraser(self):

        annots = self.getAnnotsAtPoints(self.eraserPoints)

        for annot in annots:
            self.deleteAnnot(annot)
    #-----------------------------------------------------------------------
    # Draw
    #-----------------------------------------------------------------------


    def startDraw(self, qpos):
        self.ongoingEdit = True
        self.startPos = qpos

        self.drawPoints = []

    def stopDraw(self, qpos):
        self.ongoingEdit = False

        self.applyDrawPoints()

        self.drawPoints = []

    def updateDrawPoints(self, qpos):
        '''
        Called updates the currently ongoing marking to match the latest, provided position
        '''
        fPoint = self.qPointToFloatParirs(qpos)
        self.drawPoints.append(fPoint)

    def applyDrawPoints(self):

        # self.kalman.initKalman(self.qPointToFloatParirs(self.startPos))

        # self.drawPoints = self.kalman.applyKalman(self.drawPoints)

        self.drawPoints = self.savgol.applySavgol(self.drawPoints)  # Line smoothing
        # self.estPoints = self.formEstimator.estimateLine(self.drawPoints)


        g = []
        g.append(self.drawPoints)

        annot = self.page.addInkAnnot(g)

        cyan  = norm_rgb.main
        black  = norm_rgb.black

        # let it look a little nicer
        annot.setBorder({"width":1})# line thickness, some dashing
        annot.setColors({"stroke":black})         # make the lines blue
        annot.update()

    def calculateTextRectBounds(self, content):
        '''
        Calculates the optimal rect boundaries for the desired content
        '''

        numOfLines = content.count('\n')+1
        try:
            fontwidth = pdf_annots.defaultTextSize * (int(Preferences.data['textSize'])/100)
        except ValueError:
            fontwidth = pdf_annots.defaultTextSize

        try:
            suggestedWidth = pdf_annots.defaultBoxWidth * (int(Preferences.data['textSize'])/100)
        except ValueError:
            suggestedWidth = pdf_annots.defaultBoxWidth

        try:
            suggestedHeight = pdf_annots.defaultBoxHeight * numOfLines * (int(Preferences.data['textSize'])/100)
        except ValueError:
            suggestedHeight = pdf_annots.defaultBoxHeight


        # while defaultWidth == suggestedWidth or suggestedHeight > suggestedWidth:

        #     suggestedWidth += suggestedHeight

        #     for line in content.split('\n'):
        #         delta = len(line) * fontwidth - suggestedWidth
        #         if delta > 0:
        #             suggestedHeight += (delta / suggestedWidth) * defaultHeight
        for line in content.split('\n'):
                delta = len(line) * fontwidth / suggestedWidth
                if delta > 0:
                    suggestedHeight *= delta

        return float(suggestedHeight), float(suggestedWidth)

    def calculateTextRectPos(self, frect):
        '''
        Checks that the boundaries of the provided rect do not exceed page boundaries.
        It returns the closest rect, which would meet this requirement
        '''
        # Check for x
        if frect.x1 > self.wOrigin:
            deltaX = frect.x1 - self.wOrigin
            frect.x1 -= deltaX
            frect.x0 -= deltaX
        elif frect.x0 < 0:
            deltaX = self.xOrigin
            frect.x1 += deltaX
            frect.x0 += deltaX

        # Check for y
        if frect.y1 > self.hOrigin:
            deltaY = frect.y1 - self.hOrigin
            frect.y1 -= deltaY
            frect.y0 -= deltaY
        elif frect.y0 < 0:
            deltaY = self.yOrigin
            frect.y1 += deltaY
            frect.y0 += deltaY

        return frect

    def getAnnotAtPos(self, qpos):
        '''
        Return the annot of the current page which is the first at the desired position
        '''
        for annot in self.page.annots():
            if self.pointInArea(qpos, annot.rect):
                return annot

        return None

    def getAnnotsAtPoints(self, qposList):
        '''
        Return the annots of the current page which are hitted by the any point in the list
        '''
        annots = []

        for annot in self.page.annots():
            for qpos in qposList:
                if self.pointInArea(qpos, annot.rect):
                    annots.append(annot)
                    break

        return annots

    def getAnnotWithXref(self, xRef):
        '''
        Return the annot of the current page, which matches the provided xRef
        '''
        for annot in self.page.annots():
            if annot.xref == xRef:
                return annot

        return None

    def getTextBoxContent(self, qpos):
        '''
        Return the content of the annot of the current page which is the first at the desired position
        '''
        for annot in self.page.annots(types=(fitz.PDF_ANNOT_FREE_TEXT, fitz.PDF_ANNOT_TEXT)):
            if self.pointInArea(qpos, annot.rect):
                info = annot.info

                return info["content"]

        return None

    def pointInArea(self, qpos, frect):
        '''
        Checks if the provided point is insided the rect
        '''
        if qpos.x() < frect.x0 or qpos.y() < frect.y0:
            return False

        if qpos.x() > frect.x1 or qpos.y() > frect.y1:
            return False

        return True

    def resetEditMode(self):
        '''
        Simply abstracts the process clearing the current edit mode to prevent a elevation of method access rights to global variables
        '''
        global editMode
        editMode = editModes.none

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
            if editMode == editModes.marker:
                self.startMarkText(self.toPdfCoordinates(event.pos()))
            elif editMode == editModes.freehand:
                self.startDraw(self.toPdfCoordinates(event.pos()))
            elif editMode == editModes.eraser:
                self.startEraser(self.toPdfCoordinates(event.pos()))
            elif editMode == editModes.markdown:
                scenePoint = self.toSceneCoordinates(event.pos())
                self.eh.addIndicatorPoint.emit(scenePoint.x(), scenePoint.y())

                self.startNewMarkdownBox(self.toPdfCoordinates(event.pos()))
            elif editMode == editModes.newTextBox:
                scenePoint = self.toSceneCoordinates(event.pos())
                self.eh.addIndicatorPoint.emit(scenePoint.x(), scenePoint.y())

                self.startNewTextBox(self.toPdfCoordinates(event.pos()))
        elif event.button() == Qt.RightButton:
            # Check if there is not currently an active editing mode
            if editMode == editModes.none:
                # Now, check if there is an object under the curser
                annot = self.getAnnotAtPos(self.toPdfCoordinates(event.pos()))
                if annot:
                    scenePoint = self.toSceneCoordinates(event.pos())
                    self.eh.addIndicatorPoint.emit(scenePoint.x(), scenePoint.y())

                    # Start moving this obj
                    self.startMoveObject(self.toPdfCoordinates(event.pos()), annot)

    def mouseReleaseEvent(self, event):
        '''
        Overrides the default event
        '''
        global editMode
        self.blockEdit = False

        if event.button() == Qt.LeftButton:
            if editMode == editModes.newTextBox:
                scenePoint = self.toSceneCoordinates(event.pos())
                self.eh.addIndicatorPoint.emit(scenePoint.x(), scenePoint.y())

                self.stopNewTextBox(self.toPdfCoordinates(event.pos()))
            elif editMode == editModes.markdown:
                scenePoint = self.toSceneCoordinates(event.pos())
                self.eh.addIndicatorPoint.emit(scenePoint.x(), scenePoint.y())

                self.stopNewMarkdownBox(self.toPdfCoordinates(event.pos()))

            elif editMode == editModes.marker:
                self.stopMarkText(self.toPdfCoordinates(event.pos()))
            elif editMode == editModes.freehand:
                self.stopDraw(self.toPdfCoordinates(event.pos()))
            elif editMode == editModes.eraser:
                self.stopEraser(self.toPdfCoordinates(event.pos()))

        elif event.button() == Qt.RightButton:
            #Check if there is currently an ongoing edit (like moving an object)
            if self.ongoingEdit:
                self.eh.deleteLastIndicatorPoint.emit()
                # Stop moving the object
                self.stopMoveObject(self.toPdfCoordinates(event.pos()))

            #If there was no delta shift in start and end pos, the user don't want to move the annot
            if self.startPos == self.endPos:
                # Check if there is an object under the curser
                relCorrdinates = self.toPdfCoordinates(event.pos())
                curContent = self.getTextBoxContent(self.toPdfCoordinates(event.pos()))
                if curContent:
                    annot = self.getAnnotAtPos(self.toPdfCoordinates(event.pos()))
                    self.visualizeCorners(annot)

                    # Start requesting edit text box
                    editMode = editModes.editTextBox
                    self.eh.requestTextInput.emit(relCorrdinates.x(), relCorrdinates.y(), self.pageNumber, curContent)

    def visualizeCorners(self, annot):
        rect = annot.rect
        tl = self.toSceneCoordinates(self.toQPos(rect.tl))
        tr = self.toSceneCoordinates(self.toQPos(rect.tr))
        bl = self.toSceneCoordinates(self.toQPos(rect.bl))
        br = self.toSceneCoordinates(self.toQPos(rect.br))


        self.eh.addIndicatorPoint.emit(tl.x()-6, tl.y()-6)
        self.eh.addIndicatorPoint.emit(tr.x()-3, tr.y()-6)
        self.eh.addIndicatorPoint.emit(bl.x()-6, bl.y()-2)
        self.eh.addIndicatorPoint.emit(br.x()-3, br.y()-2)

    def removeVisualCorners(self):
        self.eh.deleteLastIndicatorPoint.emit()
        self.eh.deleteLastIndicatorPoint.emit()
        self.eh.deleteLastIndicatorPoint.emit()
        self.eh.deleteLastIndicatorPoint.emit()

    def mouseMoveEvent(self, event):
        '''
        Overrides the default event
        '''
        self.blockEdit = False

        if self.ongoingEdit and not bool(Preferences.data['radioButtonPenOnly']):
            if editMode == editModes.freehand:
                self.updateDrawPoints(self.toPdfCoordinates(event.pos()))
            elif editMode == editModes.eraser:
                self.updateEraserPoints(self.toPdfCoordinates(event.pos()))
            print('test')

        QGraphicsPixmapItem.mouseMoveEvent(self, event)

    def tabletEvent(self, pos):
        self.blockEdit = False

        if self.ongoingEdit and bool(Preferences.data['radioButtonPenOnly']):

            if editMode == editModes.freehand:
                self.updateDrawPoints(self.mapFromScene(self.toPdfCoordinates(pos)))
            elif editMode == editModes.eraser:
                self.updateEraserPoints(self.toPdfCoordinates(pos))

    def toPdfCoordinates(self, qPos):
        '''
        Converts the provided position to relative pdf file coordinates
        '''
        xDif = self.x() - self.xOrigin
        yDif = self.y() - self.yOrigin
        pPos = QPoint(qPos.x() + xDif, qPos.y() + yDif)

        return pPos

    def toSceneCoordinates(self, qPos):
        xDif = self.xOrigin
        yDif = self.yOrigin
        sPos = QPoint(qPos.x() + xDif, qPos.y() + yDif)

        return sPos

    def toQPos(self, fPos):
        qPos = QPoint(fPos.x, fPos.y)

        return qPos


class GraphicsViewHandler(QGraphicsView):
    pages = IndexedOrderedDict()
    DEFAULTPAGESPACE = 20
    CONTINOUSVIEW = True

    absZoomFactor = float(1)
    lowResZoomFactor = float(0.1)

    # x, y, pageNumber, currentContent
    requestTextInput = pyqtSignal(int, int, int, str)

    tempObj = list()

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
        # self.setRenderHint(QPainter.Anti)
        self.setAttribute(Qt.WA_AcceptTouchEvents)
        # self.setDragMode(self.ScrollHandDrag)
        self.setFrameShape(QGraphicsView.NoFrame)
        # # self.resize(parent.size())
        # self.grabGesture(Qt.PanGesture)
        # self.grabGesture(Qt.PinchGesture)
        # self.grabGesture(Qt.SwipeGesture)
        # self.grabGesture(Qt.TapAndHoldGesture)
        # self.grabGesture(Qt.TapGesture)

    def __del__(self):
        self.saveCurrentPdf()

    def createNewPdf(self, fileName):
        '''
        Creates a new PDf from the given fileName
        '''
        self.pdf.newPdf(fileName)

        self.loadPdfToCurrentView(fileName)

    def saveCurrentPdf(self):
        '''
        Just handles saving the pdf
        '''
        if self.pdf.filename:
            self.pdf.savePdf()
            print('PDF saved')

    def saveCurrentPdfAs(self, fileName):
        '''
        Just handles saving the pdf
        '''
        self.pdf.savePdfAs(fileName)
        print('PDF saved as\t' + fileName)

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

        width, height = self.pdf.getPageSize(self.pdf.doc)

        for pIt in range(self.pdf.doc.pageCount):

            if pIt > 2:
                posX, posY = self.loadBlankImageToCurrentView(pIt, posX, posY, width, height)
            else:
                # Load each page to a new position in the current view.
                posX, posY = self.loadPdfPageToCurrentView(pIt, posX, posY, self.absZoomFactor)

        print("--- Loaded PDF within %s seconds ---" % (time.time() - start_time))

    def loadBlankImageToCurrentView(self, pageNumber, posX, posY, width, height):
        '''
        Creates a qpdf instance and loads an empty image.
        This is intended to be used in combination with the initial pdf loading
        '''
        # Create a qpdf instance
        pdfView = QPdfView()
        pdfView.setPage(self.pdf.getPage(pageNumber), pageNumber)

        # Render a blank image
        self.updateEmptyPdf(pdfView, width, height, pageNumber)

        # Store instance locally
        self.pages[pageNumber] = pdfView

        # Connect event handlers
        self.pages[pageNumber].eh.requestTextInput.connect(self.toolBoxTextInputRequestedEvent)
        self.pages[pageNumber].eh.addIndicatorPoint.connect(self.addIndicatorPoint)
        self.pages[pageNumber].eh.deleteLastIndicatorPoint.connect(self.deleteLastIndicatorPoint)

        # add and arrange the new page in the scene
        self.scene.addItem(self.pages[pageNumber])
        self.pages[pageNumber].setPos(posX, posY)

        # some stuff to tell the instance that the current position is the original one
        pdfView.setAsOrigin()

        return posX, posY + pdfView.hOrigin + self.DEFAULTPAGESPACE

    def loadPdfPageToCurrentView(self, pageNumber, posX, posY, zoom = None):
        '''
        Creates a qpdfView instance from the desired page and renders it at the provided position with the zoomfactor.
        A lower zoomFactor will dramatically improve speed, as it always correlates to the dpi of the page
        '''
        # Create a qpdf instance
        pdfView = QPdfView()
        pdfView.setPage(self.pdf.getPage(pageNumber), pageNumber)

        # Render according to the parameters
        self.updatePdf(pdfView, zoom = zoom, pageNumber = pageNumber)

        # Store instance locally
        self.pages[pageNumber] = pdfView

        # Connect event handlers
        self.pages[pageNumber].eh.requestTextInput.connect(self.toolBoxTextInputRequestedEvent)
        self.pages[pageNumber].eh.addIndicatorPoint.connect(self.addIndicatorPoint)
        self.pages[pageNumber].eh.deleteLastIndicatorPoint.connect(self.deleteLastIndicatorPoint)

        # add and arrange the new page in the scene
        self.scene.addItem(self.pages[pageNumber])
        self.pages[pageNumber].setPos(posX, posY)

        # some stuff to tell the instance that the current position is the original one
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

    def updateEmptyPdf(self, pdf, width, height, pageNumber = None):
        '''
        Update the provided pdf file at the desired page to render only the zoom and clip
        This methods is used when instantiating the pdf and later, when performance optimzation and zooming is required
        '''

        qImg = QImage(width, height, QImage.Format_Mono)
        qImg.fill(0)

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

            zoomInFactor = 1.1
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

    def event(self, event):
        # print(type(event))
        if type(event) == QTouchEvent:
            self.touchEvent(event)


        return super(GraphicsViewHandler, self).event(event)


    def touchEvent(self, event):
        print('touch')

    def tabletEvent(self, event):

        item = self.itemAt(event.pos())
        if type(item) == QPdfView:
            item.tabletEvent(event.pos())
        return super(GraphicsViewHandler, self).tabletEvent(event)

    def mapToItem(self, pos, item):
        rect = self.mapToScene(self.viewport().geometry()).boundingRect()
        # Store those properties for easy access
        viewportHeight = rect.height()
        viewportWidth = rect.width()
        viewportX = rect.x()
        viewportY = rect.y()

        newPos = QPoint(pos.x() + viewportX - item.x(), pos.y() - viewportY - item.y())

        return newPos

    def pageInsertHere(self):
        # Get all visible pages
        try:
            renderedItems = self.scene.items(self.mapToScene(self.viewport().geometry()))
        except Exception as e:
            return

        # Iterate all visible items (shouldn't be that much normally)
        for renderedItem in renderedItems:
            # Check if we have a pdf view here (visible could be anything)
            if type(renderedItem) != QPdfView:
                continue

            newPage = self.pdf.insertPage(renderedItem.pageNumber)

            for pIt in range(len(self.pages),0):
                if pIt == renderedItem.pageNumber + 1:
                    self.loadPdfPageToCurrentView(pIt, renderedItem.xOrigin, renderedItem.yOrigin, self.absZoomFactor)
                    break
                else:
                    self.pages[pIt] = self.pages[pIt-1]


            break





    def pageDeleteActive(self):
        pass

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

    @pyqtSlot(str)
    def editModeChangeRequest(self, editModeUpdate):
        global editMode

        editMode = editModeUpdate

    @pyqtSlot(int, int)
    def addIndicatorPoint(self, x, y):
        self.tempObj.append(QGraphicsEllipseItem(x,y,8,8))
        self.tempObj[-1].setBrush(QBrush(QColor(*rgb.fore), style = Qt.SolidPattern))
        self.scene.addItem(self.tempObj[-1])

    @pyqtSlot()
    def deleteLastIndicatorPoint(self):
        try:
            self.scene.removeItem(self.tempObj[-1])
            del self.tempObj[-1]
        except IndexError as ie:
            # Don't judge me, but this can happen
            pass
        except Exception as e:
            print(e.with_traceback())
