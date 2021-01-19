# ---------------------------------------------------------------
# -- UNote Core File --
#
# Implements core functionality
#
# Author: Melvin Strobl
# ---------------------------------------------------------------
import os
import sys
import time
from queue import Queue

from indexed import IndexedOrderedDict
from enum import Enum

from PySide2.QtWidgets import QFrame, QGraphicsView, QGraphicsScene, QApplication, QGraphicsPixmapItem, QGraphicsLineItem, QGraphicsEllipseItem, QScroller, QScrollerProperties
from PySide2.QtCore import Qt, QRectF, QEvent, QThread, Signal, Slot, QObject, QPoint, QPointF, QTimer, QByteArray, QBuffer, QIODevice
from PySide2.QtGui import QPixmap, QBrush, QColor, QImage, QTouchEvent, QPainter, QGuiApplication, QPen, QTabletEvent
# from PySide2.QtWebEngineWidgets import QWebEngineView

import fitz

from preferences import Preferences

from pdfEngine import pdfEngine
from imageHelper import imageHelper
from markdownHelper import markdownHelper

from util import toBool
from editHelper import editModes
from filters import Savgol, FormEstimator
from historyHandler import History

# sys.path.append('./style')
from style.styledef import rgb, norm_rgb, pdf_annots

editMode = editModes.none

class ExtQPoint(QPoint):
    pressure = 0


class textModes():
    plainText = 'plainText'
    mdText = 'markdownText'

class EventHelper(QObject):
    '''
    This class is intended to extend an existing qt class which does not directly inherit from qobject and therefore does not contain signaling
    '''
    # x, y, pageNumber, currentContent
    requestTextInput = Signal(int, int, int, str)
    addIndicatorPoint = Signal(int, int)
    deleteLastIndicatorPoint = Signal()

    settingsChanged = Signal()

PRESSUREMULTIPLIER = 1.6

class QPdfView(QGraphicsPixmapItem):

    def __init__(self):
        QGraphicsPixmapItem.__init__(self)
        self.blockEdit = False
        self.ongoingEdit = False

        self.eh = EventHelper()

        self.savgol = Savgol()
        self.formEstimator = FormEstimator()

        self.drawPoints = Queue()
        self.tempPoints = Queue()

        self.startPos = 0
        self.endPos = 0
        self.ongoingEdit = False
        self.blockEdit = False

        self.formPoints = []
        self.drawIndicators = []

        self.lastZoomFactor = -1

        self.isDraft = False

        self.avPressure = 1

        # Trigger this before any paint events occur
        self.settingsChangedReceiver()


    def paint(self, painter, option, widget):
        res = super().paint(painter, option, widget)

        if self.tempPoints.qsize() > 0:
            if editMode == editModes.freehand or editMode == editModes.none:
                # if Preferences.data['comboBoxThemeSelect'] == 0 and toBool(Preferences.data['radioButtonAffectsPDF']) == True:
                #     try:
                #         color = tuple(map(lambda x: (1-float(x))*255, Preferences.data['freehandColor']))
                #     except ValueError as identifier:
                #         color = rgb.white
                # else:
                #     try:
                #         color = tuple(map(lambda x: float(x)*255, Preferences.data['freehandColor']))
                #     except ValueError as identifier:
                #         color = rgb.black

                try:

                    penSize = self.avPressure / self.drawPoints.qsize() * PRESSUREMULTIPLIER * self.freeHandSize
                except ValueError:
                    penSize = pdf_annots.defaultPenSize
                except ZeroDivisionError:
                    penSize = pdf_annots.defaultPenSize


                painter.setPen(QPen(QColor(*self.freeHandColor), penSize))
                painter.setRenderHint(QPainter.SmoothPixmapTransform)
                painter.drawPolyline(list(self.tempPoints.queue))

            elif editMode == editModes.marker:

                painter.setPen(QPen(QColor(*self.markerColor), self.markerSize))
                painter.setRenderHint(QPainter.SmoothPixmapTransform)
                painter.drawPolyline(list(self.tempPoints.queue))

            elif editMode == editModes.forms:

                painter.setPen(QPen(QColor(*self.formColor), self.formSize))
                painter.setRenderHint(QPainter.SmoothPixmapTransform)
                lst = list(self.tempPoints.queue)
                painter.drawLine(lst[0],lst[-1])

        return res

    def settingsChangedReceiver(self):
        if Preferences.data['comboBoxThemeSelect'] == 0 and toBool(Preferences.data['radioButtonAffectsPDF']) == True:
            try:
                self.freeHandColor = tuple(map(lambda x: (1-float(x))*255, Preferences.data['freehandColor']))
            except ValueError as identifier:
                self.freeHandColor = rgb.white
        else:
            try:
                self.freeHandColor = tuple(map(lambda x: float(x)*255, Preferences.data['freehandColor']))
            except ValueError as identifier:
                self.freeHandColor = rgb.black

        try:

            self.freeHandSize = pdf_annots.defaultPenSize * (int(Preferences.data['freehandSize'])/pdf_annots.freeHandScale)
        except ValueError:
            self.freeHandSize = pdf_annots.defaultPenSize
        except ZeroDivisionError:
            self.freeHandSize = pdf_annots.defaultPenSize

        #------------------------------------------

        if Preferences.data['comboBoxThemeSelect'] == 0 and toBool(Preferences.data['radioButtonAffectsPDF']) == True:
            try:
                self.markerColor = tuple(map(lambda x: (1-float(x))*255, Preferences.data['markerColor']))
            except ValueError as identifier:
                self.markerColor = rgb.white
        else:
            try:
                self.markerColor = tuple(map(lambda x: float(x)*255, Preferences.data['markerColor']))
            except ValueError as identifier:
                self.markerColor = rgb.black

        try:
            self.markerSize = pdf_annots.defaultPenSize * (int(Preferences.data['markerSize'])/pdf_annots.freeHandScale)
        except ValueError:
            self.markerSize = pdf_annots.defaultPenSize

        #------------------------------------------

        if Preferences.data['comboBoxThemeSelect'] == 0 and toBool(Preferences.data['radioButtonAffectsPDF']) == True:
            try:
                self.formColor = tuple(map(lambda x: (1-float(x))*255, Preferences.data['formColor']))
            except ValueError as identifier:
                self.formColor = rgb.white
        else:
            try:
                self.formColor = tuple(map(lambda x: float(x)*255, Preferences.data['formColor']))
            except ValueError as identifier:
                self.formColor = rgb.black

        try:
            self.formSize = pdf_annots.defaultPenSize * (int(Preferences.data['formSize'])/pdf_annots.freeHandScale)
        except ValueError:
            self.formSize = pdf_annots.defaultPenSize




    def setPixMap(self, qImg, pageNumber, newZoomFactor=1):
        self.pageNumber = pageNumber

        self.updatePixMap(qImg)

        self.lastZoomFactor = newZoomFactor

    def updatePixMap(self, qImg, newZoomFactor=1):
        self.qImg = qImg

        self.pixImg = QPixmap()
        # self.draftImg = QPixmap()

        self.pixImg.convertFromImage(self.qImg)

        self.setPixmap(self.pixImg)

        self.lastZoomFactor = newZoomFactor

    def setAsDraft(self):
        self.isDraft = True

    def setAsOrigin(self):
        self.xOrigin = self.x()
        self.yOrigin = self.y()

        self.wOrigin = self.boundingRect().width()
        self.hOrigin = self.boundingRect().height()

    def getStartPos(self):
        return (self.xOrigin, self.yOrigin)

    def getEndPos(self):
        return (self.xOrigin + self.wOrigin, self.yOrigin + self.hOrigin)

    def getSize(self):
        return (self.wOrigin, self.hOrigin)

    def setPage(self, page, pageNumber):
        self.page = page
        # print(page.rotationMatrix)
        self.pageNumber = pageNumber


    def reloadQImg(self, zoomFactor):
        mat = fitz.Matrix(zoomFactor, zoomFactor)
        self.pixImg.convertFromImage(self.qImg)

    def qPointToFPoint(self, qPoint):
        return fitz.Point(qPoint.x(), qPoint.y())

    def qPointToFloatParirs(self, qPoint, pressure=0):
        p = (float(qPoint.x()), float(qPoint.y()), pressure)
        return p

    def fPointToQPoint(self, fPoint):
        return QPoint(fPoint.x, fPoint.y)

    def qPointDistance(self, qPosA, qPosB):
        return abs(qPosA[0] - qPosB[0]) + abs(qPosA[1] - qPosB[1])

    #-----------------------------------------------------------------------
    # Markdown Box
    #-----------------------------------------------------------------------

    def startNewMarkdownBox(self, qpos):
        self.ongoingEdit = True
        self.startPos = qpos

    def stopNewMarkdownBox(self, qpos):
        self.ongoingEdit = False
        self.endPos = qpos

        # self.eh.requestTextInput.emit(self.endPos.x(), self.endPos.y(), self.pageNumber, "")

    def insertMarkdown(self, qpos, content):
        self.preview = QWebEngineView()

        self.mdHelper = markdownHelper()

        self.page = self.mdHelper.loadGetMarkdownPage(content)

        self.preview.setPage(self.page)


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

                nAnnot = self.addArrow(fStart, fEnd, "")

                textAnnotInfo = textAnnot.info
                textAnnotInfo["subject"] = str(nAnnot.xref)
                textAnnot.setInfo(textAnnotInfo)

                self.eh.deleteLastIndicatorPoint.emit()

            self.eh.deleteLastIndicatorPoint.emit()

            textAnnot.update()

            History.addToHistory(self.deleteText, textAnnot, self.insertText, (qpos, content))

        else:
            # Only when there is a line
            if self.startPos != self.endPos:
                self.eh.deleteLastIndicatorPoint.emit()

    def deleteText(self, annot):
        self.deleteAnnot(annot)


    def addArrow(self, fStart, fEnd, subj):
        cyan  = norm_rgb.main
        borderLine = {"width": pdf_annots.borderWidth}

        lineAnnot = self.page.addLineAnnot(fStart, fEnd)

        lineAnnotInfo = lineAnnot.info
        lineAnnotInfo["subject"] = subj
        lineAnnot.setInfo(lineAnnotInfo)

        lineAnnot.setBorder(borderLine)
        lineAnnot.setLineEnds(fitz.PDF_ANNOT_LE_CIRCLE , fitz.PDF_ANNOT_LE_CIRCLE)
        lineAnnot.update(border_color=cyan, fill_color=cyan)
        lineAnnot.update()

        return lineAnnot

    def addLine(self, fStart, fEnd, subj):
        # fStart, fEnd, subj = line

        try:
            borderLine = {"width": pdf_annots.lineWidth * (int(Preferences.data['formSize'])/100)}
        except ValueError:
            borderLine = {"width": pdf_annots.lineWidth}

        lineAnnot = self.page.addLineAnnot(fStart, fEnd)

        lineAnnotInfo = lineAnnot.info
        lineAnnotInfo["subject"] = subj
        lineAnnot.setInfo(lineAnnotInfo)

        lineAnnot.setBorder(borderLine)

        try:
            lineColor = tuple(map(lambda x: float(x), Preferences.data['formColor']))
        except ValueError as identifier:
            lineColor = norm_rgb.main

        lineAnnot.setColors({"stroke":lineColor})
        lineAnnot.update()

        return lineAnnot

    def deleteLine(self, annot):
        self.deleteAnnot(annot)

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

    #-----------------------------------------------------------------------
    # Images
    #-----------------------------------------------------------------------

    def insertImage(self, qPos, zoom, qPixmap):
        start = self.qPointToFPoint(qPos)
        stop = fitz.Point(start.x + qPixmap.width() / zoom, start.y + qPixmap.height() / zoom)
        rect = fitz.Rect(start.x, start.y, stop.x, stop.y)

        fPixmap = self.qPixmapTofPixmap(qPixmap)

        prevList = self.page.getImageList()

        self.page.insertImage(rect, pixmap=fPixmap, overlay=True)

        # latestList = self.page.getImageList()
        # newImageEntry = [value for value in latestList if value not in prevList][0]

        # if newImageEntry[8] == '':
        #     ref = newImageEntry[8]
        # else:
        #     ref = newImageEntry[7]

        # pass

    #-----------------------------------------------------------------------
    # Annot Editing
    #-----------------------------------------------------------------------

    def addAnnot(self, annot):
        try:
            self.page.addAnnot(annot)
        except Exception as identifier:
            print("Unable to add annot")

    def deleteAnnot(self, annot):
        '''
        Deletes the desired annot and the corresponding line if one is found
        '''
        # Check if there is a corresponding line annot
        corrAnnot = self.getCorrespondingAnnot(annot)
        if corrAnnot:
            try:
                self.page.deleteAnnot(corrAnnot)
            except ValueError as identifier:
                print(str(identifier))

        try:
            self.page.deleteAnnot(annot)
        except ValueError as identifier:
            print(str(identifier))

    def getCorrespondingAnnot(self, annot):
        try:
            info = annot.info
        # Parent orphaned
        except ValueError as identifier:
            return None

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

        # Catch in case curr annot is not defined yet
        try:
            self.currAnnot = self.moveAnnotByDelta(self.startPos, self.endPos, self.currAnnot)
        except AttributeError as identifier:
            print(str(identifier))

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
            nAnnot = self.addArrow(fStart, fEnd, lineSubj)

            textInfo = annot.info
            textInfo["subject"] = str(nAnnot.xref)
            annot.setInfo(textInfo)
            annot.update()

        return annot

    #-----------------------------------------------------------------------
    # Marker
    #-----------------------------------------------------------------------

    def startMarkText(self, qpos):
        self.ongoingEdit = True
        self.startPos = self.qPointToFPoint(qpos)
        # self.startPos = qpos

    def stopMarkText(self, qpos):
        self.ongoingEdit = False
        self.endPos = self.qPointToFPoint(qpos)
        # self.endPos = qpos

        self.updateMarkText()

    def updateMarkText(self):
        '''
        Called updates the currently ongoing marking to match the latest, provided position
        '''
        # self.startPos = self.startPos * self.page.derotationMatrix
        # self.endPos = self.endPos * self.page.derotationMatrix

        yMin = min(self.startPos.y, self.endPos.y)
        yMax = max(self.startPos.y, self.endPos.y)

        try:
            minWidth = pdf_annots.defaultMarkerSize * (int(Preferences.data['markerSize'])/pdf_annots.markerScale)
        except ValueError:
            minWidth = pdf_annots.defaultMarkerSize

        # Ensure at least a width of 10
        if abs(yMin - yMax) < minWidth:
            yMin = yMin - minWidth/2
            yMax = yMax + minWidth/2

        xMin = min(self.startPos.x, self.endPos.x)
        xMax = max(self.startPos.x, self.endPos.x)


        dx = xMax - xMin
        dy = yMax - yMin

        rect = fitz.Rect(xMin, yMin, xMax, yMax)

        if dx < dy:
            rect = rect.transform(self.page.derotationMatrix)
            # rect = fitz.Rect(xMin, yMax, xMax, yMin)

        annot = self.addHighlightAnnot(rect)

        History.addToHistory(self.deleteHighlightAnnot, annot, self.addHighlightAnnot, rect)


    def addHighlightAnnot(self, rect):
        annot = self.page.addHighlightAnnot(rect)

        try:
            markerColor = tuple(map(lambda x: float(x), Preferences.data['markerColor']))
        except ValueError as identifier:
            markerColor = norm_rgb.main

        annot.setColors({"stroke":markerColor})         # make the lines blue
        annot.update()

        return annot

    def deleteHighlightAnnot(self, annot):
        self.deleteAnnot(annot)

    #-----------------------------------------------------------------------
    # Eraser
    #-----------------------------------------------------------------------


    def startEraser(self, qpos):
        self.ongoingEdit = True

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
            # History.addToHistory(self.addAnnot, annot, self.deleteAnnot, annot)
            self.deleteAnnot(annot)


    #-----------------------------------------------------------------------
    # Draw
    #-----------------------------------------------------------------------
    def startForms(self, qpos):
        self.ongoingEdit = True

        self.formPoints = []

    def stopForms(self, qpos):
        self.applyFormPoints()
        # self.drawIndicators = []

        self.ongoingEdit = False

    def updateFormPoints(self, qpos):
        self.formPoints.append(self.qPointToFPoint(qpos)*self.page.derotationMatrix)


    def applyFormPoints(self):
        fStart, fStop = self.formEstimator.estimateLine(self.formPoints[0], self.formPoints[-1])

        annot = self.addLine(fStart, fStop, "")

        History.addToHistory(self.deleteLine, annot, self.addLine, (fStart, fStop, ""))

    #-----------------------------------------------------------------------
    # Draw
    #-----------------------------------------------------------------------
    def startDraw(self, qpos, pressure=0):
        if self.ongoingEdit:
            return
        self.ongoingEdit = True

        # self.drawIndicators = []
        # self.drawPoints.append(self.qPointToFloatParirs(qpos, pressure))

    def stopDraw(self, qpos, pressure=0):

        # fPoint = self.qPointToFloatParirs(qpos)
        # self.drawPoints.append(fPoint)

        self.applyDrawPoints()
        # self.drawIndicators = []


    def updateDrawPoints(self, qpos, pressure=0):
        '''
        Called updates the currently ongoing marking to match the latest, provided position
        '''

        curPos = self.qPointToFloatParirs(qpos, pressure)

        # if len(self.drawPoints) > 1 and self.qPointDistance(self.drawPoints[-1], curPos) > 30:
        #     with self.drawPoints.mutex:
        #         self.drawPoints.queue.clear()

        self.drawPoints.put(curPos)
        # self.drawIndicators.append(qpos)


        self.avPressure += pressure

    def applyDrawPoints(self):

        # self.kalman.initKalman(self.qPointToFloatParirs(self.startPos))

        # self.drawPoints = self.kalman.applyKalman(self.drawPoints)
        segment = list(self.drawPoints.queue)

        with self.drawPoints.mutex:
            self.drawPoints.queue.clear()


        self.ongoingEdit = False


        # Line smoothing
        # self.estPoints = self.formEstimator.estimateLine(self.drawPoints)

        pointList = list()
        for point in segment:
            fp = fitz.Point(point[0], point[1])
            fpt = fp * self.page.derotationMatrix
            pointList.append([fpt.x, fpt.y])


        pointList = [pointList]

        # pressure = []

        # for point in points:
        #     pressure.append(point[2])

        annot = self.addInkAnnot(pointList, self.avPressure)
        History.addToHistory(self.deleteInkAnnot, annot, self.addInkAnnot, (pointList, self.avPressure))

        self.avPressure = 1

    def addInkAnnot(self, pointList, pressure = None):
        # if pressureList:
        #     it = 0
        #     for it in range(len(pointList[0])):
        #         if pressureList[it] > 0.04:
        #             pointList[0][it][1]

        try:
            annot = self.page.addInkAnnot(pointList)
        except RuntimeError as identifier:
            print(str(identifier))
            return
        except ValueError:
            return

        try:
            penSize = pressure / len(pointList[0]) * PRESSUREMULTIPLIER * pdf_annots.defaultPenSize * (int(Preferences.data['freehandSize'])/pdf_annots.freeHandScale)
        except ValueError:
            penSize = pdf_annots.defaultPenSize

        try:
            freehandColor = tuple(map(lambda x: float(x), Preferences.data['freehandColor']))
        except ValueError as identifier:
            freehandColor = norm_rgb.main

        annot.setBorder({"width":penSize})# line thickness, some dashing
        annot.setColors({"stroke":freehandColor})         # make the lines blue
        annot.update()

        return annot

    def deleteInkAnnot(self, annot):
        pointList = []
        pointList.append(annot.vertices)

        self.deleteAnnot(annot)

        # Currently not working quite well
        return pointList

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


        for line in content.split('\n'):
            delta = len(line) * fontwidth - suggestedWidth
            if delta > 0:
                suggestedHeight += (delta / suggestedWidth) * pdf_annots.defaultBoxHeight

        # for line in content.split('\n'):
        #         delta = len(line) * fontwidth / suggestedWidth
        #         if delta > 0:
        #             suggestedHeight *= delta
        suggestedHeight *= (int(Preferences.data['textSize'])/100)
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
        try:
            for annot in self.page.annots():
                if self.pointInArea(qpos, annot.rect):
                    return annot
        except ValueError as identifier:
            return None



        return None

    def getAnnotsAtPoints(self, qposList):
        '''
        Return the annots of the current page which are hitted by the any point in the list
        '''
        annots = []

        for annot in self.page.annots():
            for qpos in qposList:
                #TODO: Change that here
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
        try:
            for annot in self.page.annots(types=(fitz.PDF_ANNOT_FREE_TEXT, fitz.PDF_ANNOT_TEXT)):
                if self.pointInArea(qpos, annot.rect):
                    info = annot.info

                    return info["content"]
        except ValueError as identifier:
            return None

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
            if editMode == editModes.newTextBox:
                scenePoint = self.toSceneCoordinates(event.pos())
                self.eh.addIndicatorPoint.emit(scenePoint.x(), scenePoint.y())
                self.startNewTextBox(self.toPdfCoordinates(event.pos()))
            elif editMode == editModes.markdown:
                scenePoint = self.toSceneCoordinates(event.pos())
                self.eh.addIndicatorPoint.emit(scenePoint.x(), scenePoint.y())
                self.startNewMarkdownBox(self.toPdfCoordinates(event.pos()))

            if not toBool(Preferences.data['radioButtonPenDrawOnly']):
                if editMode == editModes.marker:
                    self.startMarkText(self.toPdfCoordinates(event.pos()))
                elif editMode == editModes.freehand:
                    self.startDraw(self.toPdfCoordinates(event.pos()))
                elif editMode == editModes.eraser:
                    self.startEraser(self.toPdfCoordinates(event.pos()))
                elif editMode == editModes.forms:
                    self.startForms(self.toPdfCoordinates(event.pos()))

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

            if not toBool(Preferences.data['radioButtonPenDrawOnly']):
                if editMode == editModes.marker:
                    self.stopMarkText(self.toPdfCoordinates(event.pos()))
                elif editMode == editModes.freehand:
                    self.stopDraw(self.toPdfCoordinates(event.pos()))
                    self.tempPoints = Queue()
                elif editMode == editModes.eraser:
                    self.stopEraser(self.toPdfCoordinates(event.pos()))
                elif editMode == editModes.forms:
                    self.stopForms(self.toPdfCoordinates(event.pos()))

        elif event.button() == Qt.RightButton:
            #Check if there is currently an ongoing edit (like moving an object)
            if self.ongoingEdit:
                self.eh.deleteLastIndicatorPoint.emit()
                # Stop moving the object
                self.stopMoveObject(self.toPdfCoordinates(event.pos()))

            #If there was no delta shift in start and end pos, the user don't want to move an annot
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
                # # There was no annot, so the user might want to insert something
                # else:
                #     self.insertContent()

                    # if mimeData.hasImage():
                    #     QImage = clipboard.image()
                    #     # self.insertImage(event.pos(), clipboard.pixmap())
                    # elif mimeData.hasHtml():
                    #     self.insertMarkdown(mimeData.html())
                    # elif mimeData.hasText():
                    #     self.insertText(mimeData.text())

    def insertContent(self, pos, zoom, xOff, yOff):
        clipboard = QGuiApplication.clipboard()
        mimeData = clipboard.mimeData()

        if mimeData.hasImage():
            print("Image in clipboard")
            pixmap = mimeData.imageData()
            self.insertImage(self.fromSceneCoordinates(pos, zoom, xOff, yOff), zoom, pixmap)
        elif mimeData.hasHtml():
            print("Html in clipboard")
        elif mimeData.hasText():
            print("Text in clipboard")
        else:
            print("Unknown format in clipboard")


    def mouseMoveEvent(self, event):
        '''
        Overrides the default event
        '''
        self.blockEdit = False

        if self.ongoingEdit and not toBool(Preferences.data['radioButtonPenDrawOnly']):
            if editMode == editModes.freehand:
                self.updateDrawPoints(self.toPdfCoordinates(event.pos()))
                self.tempPoints.put(self.toPdfCoordinates(event.pos()))
                self.update()
            elif editMode == editModes.eraser:
                self.updateEraserPoints(self.toPdfCoordinates(event.pos()))
            elif editMode == editModes.forms:
                self.tempPoints.put(self.toPdfCoordinates(event.pos()))
                self.update()
            elif editMode == editModes.marker:
                self.tempPoints.put(self.toPdfCoordinates(event.pos()))
                self.update()

        QGraphicsPixmapItem.mouseMoveEvent(self, event)

    def qPixmapTofPixmap(self, qPixmap):
        # mode = fitz.cs if qPixmap.hasAlphaChannel else fitz.csRGB

        bArray = QByteArray()
        buffer = QBuffer(bArray)
        buffer.open(QIODevice.ReadWrite)
        qPixmap.save(buffer, "BMP")

        cs = fitz.csRGB
        fPixmap = fitz.Pixmap(bArray.data())
        fPixmap = fitz.Pixmap(cs, fPixmap)

        return fPixmap
        # fPixmap = fitz.Pixmap(cs, qPixmap.width(), qPixmap.height(), bArray.data())

    def visualizeCorners(self, annot):
        rect = annot.rect
        tl = self.toSceneCoordinates(self.fPosToQPos(rect.tl))
        tr = self.toSceneCoordinates(self.fPosToQPos(rect.tr))
        bl = self.toSceneCoordinates(self.fPosToQPos(rect.bl))
        br = self.toSceneCoordinates(self.fPosToQPos(rect.br))


        self.eh.addIndicatorPoint.emit(tl.x()-6, tl.y()-6)
        self.eh.addIndicatorPoint.emit(tr.x()-3, tr.y()-6)
        self.eh.addIndicatorPoint.emit(bl.x()-6, bl.y()-2)
        self.eh.addIndicatorPoint.emit(br.x()-3, br.y()-2)

    def removeVisualCorners(self):
        self.eh.deleteLastIndicatorPoint.emit()
        self.eh.deleteLastIndicatorPoint.emit()
        self.eh.deleteLastIndicatorPoint.emit()
        self.eh.deleteLastIndicatorPoint.emit()


    def tabletEvent(self, eventType, pressure, highResPos, zoom, xOff, yOff):
        self.blockEdit = False
        if toBool(Preferences.data['radioButtonPenDrawOnly']):
            if eventType == QEvent.TabletMove and self.ongoingEdit:
                if editMode == editModes.eraser:
                    self.updateEraserPoints(self.fromSceneCoordinates(highResPos, zoom, xOff, yOff))
                elif editMode == editModes.forms:
                    self.updateFormPoints(self.fromSceneCoordinates(highResPos, zoom, xOff, yOff))
                    self.tempPoints.put(self.toWidgetCoordinates(highResPos, zoom, xOff, yOff))
                    self.update()
                elif editMode == editModes.marker:
                    self.tempPoints.put(self.toWidgetCoordinates(highResPos, zoom, xOff, yOff))
                    self.update()
                elif editMode == editModes.freehand or toBool(Preferences.data['radioButtonUsePenAsDefault']):
                    self.updateDrawPoints(self.fromSceneCoordinates(highResPos, zoom, xOff, yOff), pressure)
                    self.tempPoints.put(self.toWidgetCoordinates(highResPos, zoom, xOff, yOff))
                    self.update()
            elif eventType == QEvent.TabletPress:
                if editMode == editModes.marker:
                    self.startMarkText(self.fromSceneCoordinates(highResPos, zoom, xOff, yOff))
                elif editMode == editModes.eraser:
                    self.startEraser(self.fromSceneCoordinates(highResPos, zoom, xOff, yOff))
                elif editMode == editModes.forms:
                    self.startForms(self.fromSceneCoordinates(highResPos, zoom, xOff, yOff))
                elif editMode == editModes.freehand or toBool(Preferences.data['radioButtonUsePenAsDefault']):
                    self.startDraw(self.fromSceneCoordinates(highResPos, zoom, xOff, yOff))
            elif eventType == QEvent.TabletRelease:
                if editMode == editModes.marker:
                    self.stopMarkText(self.fromSceneCoordinates(highResPos, zoom, xOff, yOff))
                elif editMode == editModes.eraser:
                    self.stopEraser(self.fromSceneCoordinates(highResPos, zoom, xOff, yOff))
                elif editMode == editModes.forms:
                    self.stopForms(self.fromSceneCoordinates(highResPos, zoom, xOff, yOff))
                elif editMode == editModes.freehand or toBool(Preferences.data['radioButtonUsePenAsDefault']):
                    self.stopDraw(self.fromSceneCoordinates(highResPos, zoom, xOff, yOff))

            elif eventType == QEvent.TabletEnterProximity:
                print('enter prox')
            elif eventType == QEvent.TabletLeaveProximity:
                print('leave prox')

            # event.accept()

    def RenderingFinished(self):
        self.tempPoints = Queue()


    # def paint(self, QPainter, QStyleOptionGraphicsItem, QWidget):
    #     QPainter.begin(QWidget)
    #     QPainter.setPen(QColor(255,255,255))
    #     for point in self.drawIndicators:
    #         QPainter.drawPoint(point)
    #     QPainter.end()

    #     return super().paint(QPainter, QStyleOptionGraphicsItem, QWidget)


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

    def toWidgetCoordinates(self, qPos, zoom, xOff, yOff):
        # pPos = self.mapFromParent(qPos)
        qPos = qPos / zoom

        qPos.setX(abs(qPos.x())+xOff - self.x())
        qPos.setY(abs(qPos.y())+yOff - self.y())
        return qPos

    def singleFromSceneCoordinates(self, qPos, zoom, xOff, yOff):
        # pPos = self.mapFromParent(qPos)
        qPos = qPos / zoom

        qPos = (abs(qPos)+xOff - self.xOrigin)
        return qPos

    def fromSceneCoordinates(self, qPos, zoom, xOff, yOff):
        # pPos = self.mapFromParent(qPos)
        qPos = qPos / zoom

        qPos.setX(abs(qPos.x())+xOff - self.xOrigin)
        qPos.setY(abs(qPos.y())+yOff - self.yOrigin)
        return qPos

    def nfromSceneCoordinates(self, qPos, zoom, xOff, yOff):
        # pPos = self.mapFromParent(qPos)
        qPos = qPos / zoom

        xSug = abs(xOff - self.xOrigin) * zoom
        ySug = abs(yOff - self.yOrigin) * zoom

        qPos = QPoint(xSug, ySug)
        return qPos

    def rectFromSceneCoordinates(self, qRect, zoom, qRectOff):
        tl = self.nfromSceneCoordinates(qRect.topLeft(), zoom, qRectOff.topLeft().x(), qRectOff.topLeft().y())
        br = self.nfromSceneCoordinates(qRect.bottomRight(), zoom, qRectOff.bottomRight().x(), qRectOff.bottomRight().y())
        print(f"{self.pageNumber}: {tl} - {br} - {zoom}")

        qRect.setTopLeft(tl)
        qRect.setBottomRight(br)

        return qRect

    def cropAndAlign(self, clip, zoom, off):
        qClip = self.rectFromSceneCoordinates(clip, zoom, off)

        dx = self.wOrigin - clip.width()
        dy = self.hOrigin - clip.height()

        print(f"{dx} - {dy}")

        return qClip

    def qRectToFRect(self, qRect):
        tl = self.qPointToFPoint(qRect.topLeft())
        br = self.qPointToFPoint(qRect.bottomRight())

        fRect = fitz.Rect(tl, br)

        return fRect

    def fPosToQPos(self, fPos):
        qPos = QPoint(fPos.x, fPos.y)

        return qPos

    def posToQPos(self, x, y):
        qPos = QPoint(x, y)

        return qPos


class Renderer(QObject):
    DEFAULTPAGESPACE = 7
    LOWRESZOOM = float(0.3)

    itemRenderFinished = Signal(QPdfView, int, int)
    pdfRenderFinished = Signal()

    nextRenderingPage = 0
    enableBackgroundRendering = False

    def __init__(self, parent):
        QObject.__init__(self)

        self.pages = IndexedOrderedDict()
        self.absZoomFactor = float(1)

        self.pdf = pdfEngine()
        self.imageHelper = imageHelper()

        self.backgroundRenderTimer = QTimer()

        self.parent = parent

    def updateReceiver(self, zoom):
        self.rendererWorker.absZoomFactor = zoom

    def getPageSize(self, page=0):
        return self.pdf.getPageSize(0)

    def backgroundRenderer(self):
        for pIt in range(self.pdf.doc.pageCount):
            if pIt == (self.nextRenderingPage):
                if self.pages[pIt].isDraft:
                    print("Rendering " + str(pIt))
                    self.updatePage(self.pages[pIt], self.absZoomFactor)
                    self.nextRenderingPage = pIt + 1

                    self.enableBackgroundRenderer()
                    self.startBackgroundRenderer()
                    return
                else:
                    self.nextRenderingPage = pIt + 1

    def startBackgroundRenderer(self):
        if self.nextRenderingPage < self.pdf.doc.pageCount and self.enableBackgroundRendering:
            self.stopBackgroundRenderer()
            self.backgroundRenderTimer.singleShot(300, self.backgroundRenderer)


    def stopBackgroundRenderer(self):
        self.enableBackgroundRendering = False

    def enableBackgroundRenderer(self):
        self.enableBackgroundRendering = True

    @Slot(int)
    def renderPdfToCurrentView(self, startPage):
        self.startPage = startPage
        t = QTimer()

        t.singleShot(0, self.delayedRenderer)


    def delayedRenderer(self):
        # Start at the top
        posX = float(0)
        posY = float(0)

        width, height = self.getPageSize()

        print('Rendering PDF from page ' + str(self.startPage))
        self.start_time = time.time()

        for pIt in range(self.pdf.doc.pageCount):

            if pIt <= self.startPage + 2 and pIt >= self.startPage - 2:
                self.loadPdfPageToCurrentView(pIt, posX, posY, self.absZoomFactor)
            # elif pIt <= self.startPage + 10 and pIt >= self.startPage - 10:
            #     self.loadPdfPageToCurrentView(pIt, posX, posY, self.LOWRESZOOM)
            #     self.pages[pIt].setAsDraft()
            else:
                self.loadBlankImageToCurrentView(pIt, posX, posY, width, height)
                self.pages[pIt].setAsDraft()

            posY += height + self.DEFAULTPAGESPACE

        self.pdfRenderFinished.emit()
        self.enableBackgroundRendering = True

    def loadBlankImageToCurrentView(self, pageNumber, posX, posY, width, height):
        '''
        Creates a qpdf instance and loads an empty image.
        This is intended to be used in combination with the initial pdf loading
        '''
        # Create a qpdf instance
        pdfView = QPdfView()
        pdfView.setPage(self.pdf.getPage(pageNumber), pageNumber)

        # Render a blank image
        self.updateEmptyPdf(pdfView, width, height)

        # Store instance locally
        self.pages[pageNumber] = pdfView

        self.connectPageSignals(self.pages[pageNumber])

        # add and arrange the new page in the scene
        self.itemRenderFinished.emit(self.pages[pageNumber], posX, posY)


    def loadPdfPageToCurrentView(self, pageNumber, posX, posY, zoom):
        '''
        Creates a qpdfView instance from the desired page and renders it at the provided position with the zoomfactor.
        A lower zoomFactor will dramatically improve speed, as it always correlates to the dpi of the page
        '''
        # Create a qpdf instance
        pdfView = QPdfView()
        pdfView.setPage(self.pdf.getPage(pageNumber), pageNumber)

        # Render according to the parameters
        self.updatePage(pdfView, zoom = zoom)

        if pageNumber in self.pages:
            pagesCache = self.pages.copy()

            for pageNumberIt in sorted(pagesCache.keys(), reverse=True):
                if pageNumberIt >= pageNumber:
                    self.pages[pageNumber+1] = pagesCache[pageNumberIt]
                else:
                    break

        # Store instance locally
        self.pages[pageNumber] = pdfView

        self.connectPageSignals(self.pages[pageNumber])

        # add and arrange the new page in the scene
        self.itemRenderFinished.emit(self.pages[pageNumber], posX, posY)

    def connectPageSignals(self, page):
        # # Connect event handlers
        page.eh.requestTextInput.connect(self.parent.toolBoxTextInputRequestedEvent)
        page.eh.addIndicatorPoint.connect(self.parent.addIndicatorPoint)
        page.eh.deleteLastIndicatorPoint.connect(self.parent.deleteLastIndicatorPoint)

        self.parent.settingsChanged.connect(page.settingsChangedReceiver)

    def removePdfPageFromCurrentView(self, pdfView):
        pagesCache = self.pages.copy()

        for pageNumberIt in sorted(pagesCache.keys(), reverse=True):
            if pdfView.pageNumber < pageNumberIt:
                self.pages[pageNumberIt-1] = pagesCache[pageNumberIt]

            self.pages[pageNumberIt] = self.pdf.getPage(pageNumberIt)


        # del self.pages[self.pages.keys()[-1]]

    def updatePage(self, pdfViewInstance, zoom, clip=None, off=None):
        '''
        Update the provided pdf file at the desired page to render only the zoom and clip
        This methods is used when instantiating the pdf and later, when performance optimization and zooming is required
        '''

        # clip = None
        if clip:
            try:
                # qpos = QPoint(clip.x(), clip.y())
                # fpos = pdfViewInstance.fromSceneCoordinates(qpos, zoom, clip.x(), clip.y())
                qClip = pdfViewInstance.cropAndAlign(clip, zoom, off)
                fClip = pdfViewInstance.qRectToFRect(qClip)
                # fClip = None
            except Exception as identifier:
                fClip = None



        else:
            fClip = None

        try:
            mat = fitz.Matrix(zoom, zoom)
            pixmap = self.pdf.renderPixmap(pdfViewInstance.pageNumber, mat=mat, clip=fClip)
        except RuntimeError as identifier:
            print(str(identifier))
            return

        try:
            qImg = self.pdf.getQImage(pixmap)
        except ValueError as identifier:
            return

        qImg.setDevicePixelRatio(zoom)
        qImg = self.imageHelper.applyTheme(qImg)

        if pdfViewInstance.pageNumber:
            pdfViewInstance.setPixMap(qImg, pdfViewInstance.pageNumber, zoom)
        else:
            pdfViewInstance.updatePixMap(qImg, zoom)

        if fClip != None:
            xCorr = pdfViewInstance.xOrigin + off.x()
            yCorr = pdfViewInstance.yOrigin + off.y()

            pdfViewInstance.setPos(xCorr, yCorr)

    def updateEmptyPdf(self, pdfViewInstance, width, height):
        '''
        Update the provided pdf file at the desired page to render only the zoom and clip
        This methods is used when instantiating the pdf and later, when performance optimization and zooming is required
        '''

        qImg = QImage(1, 1, QImage.Format_Mono)
        qImg.fill(0)

        if pdfViewInstance.pageNumber:
            pdfViewInstance.setPixMap(qImg, pdfViewInstance.pageNumber)
        else:
            pdfViewInstance.updatePixMap(qImg)

class GraphicsViewHandler(QGraphicsView):
    # pages = IndexedOrderedDict()

    updatePages = Signal()
    renderPdf = Signal(int)

    # absZoomFactor = float(1)
    LOWRESZOOM = float(0.1)

    # x, y, pageNumber, currentContent
    requestTextInput = Signal(int, int, int, str)
    changesMade = Signal(bool)

    settingsChanged = Signal()

    tempObj = list()
    updateIndicator = False

    colorOverride = False

    def __init__(self, parent):
        '''
        Creates the graphic view handler instance, which is a main feature of the unote application

        :param parent: Parent editor widget.
        '''
        QGraphicsView.__init__(self, parent)

        self.gotoScrollPos = 0
        self.startPage = 0

        # self.pdf = pdfEngine()
        # self.imageHelper = imageHelper()

        self.setMouseTracking(True)
        self.setTabletTracking(True)
        # self.setFrameShape(QFrame.StyledPanel)
        self.setObjectName("graphicsView")
        self.setRenderHint(QPainter.Antialiasing)
        self.setAttribute(Qt.WA_AcceptTouchEvents)
        self.viewport().setAttribute(Qt.WA_AcceptTouchEvents)
        # self.setDragMode(self.ScrollHandDrag)
        # self.setFrameShape(QGraphicsView.NoFrame)
        # # self.resize(parent.size())


        self.scroller = QScroller.scroller(self.viewport())
        self.scroller.grabGesture(self.viewport(), QScroller.TouchGesture)
        self.scroller.stateChanged.connect(self.scrollerStateChanged)

        self.scrollerProperties = self.scroller.scrollerProperties()
        self.scrollerProperties.setScrollMetric(QScrollerProperties.VerticalOvershootPolicy, QScrollerProperties.OvershootAlwaysOff)

        self.scrollerProperties.setScrollMetric(QScrollerProperties.HorizontalOvershootPolicy, QScrollerProperties.OvershootAlwaysOff)

        self.scroller.setScrollerProperties(self.scrollerProperties)

        self.rendererThread = QThread(parent)
        self.rendererWorker = Renderer(self)

        self.setupScene()

        self.instructRenderer()


    def paintEvent(self, event):


        res = super().paintEvent(event)

        # self.rendererWorker.startBackgroundRenderer()

        return res

    def terminate(self):
        print("Terminating Viewer")

        self.rendererThread.terminate()

        if toBool(Preferences.data['radioButtonSaveOnExit']):
            if History.recentChanges != 0:
                self.saveCurrentPdf()

    def setupScene(self):
        self.scene = QGraphicsScene()
        self.setScene(self.scene)

        self.setAlignment(Qt.AlignLeft | Qt.AlignTop)


    def createNewPdf(self, fileName):
        '''
        Creates a new PDf from the given fileName
        '''
        self.rendererWorker.pdf.newPdf(fileName)

        self.loadPdfToCurrentView(fileName)

    def saveCurrentPdf(self, cleanup=True):
        '''
        Just handles saving the pdf
        '''
        if self.rendererWorker.pdf.filename:
            if History.recentChanges != 0 or cleanup == False:
                return self.rendererWorker.pdf.savePdf()
            else:
                print("Cleaning up pdf")
                return self.rendererWorker.pdf.savePdf(cleanup=True)

    def saveCurrentPdfAs(self, fileName):
        '''
        Just handles saving the pdf
        '''
        self.rendererWorker.pdf.savePdfAs(fileName)
        print('PDF saved as\t' + fileName)

    def loadPdfToCurrentView(self, pdfFilePath, startPage=0):
        '''
        Renderes the whole pdf file in the current graphic view instance
        '''
        self.start_time = time.time()

        self.rendererWorker.pdf.openPdf(pdfFilePath)

        self.renderPdfToCurrentView(startPage)

    def loadPdfInstanceToCurrentView(self, pdfInstance, startPage=0):
        self.start_time = time.time()

        self.rendererWorker.pdf = pdfInstance

        self.renderPdfToCurrentView(startPage)

    def instructRenderer(self, startPage=0):
        # self.rendererWorker.moveToThread(self.rendererThread)
        # self.rendererThread.finished.connect(QObject.deleteLater)
        self.updatePages.connect(self.rendererWorker.updateReceiver)
        self.renderPdf.connect(self.rendererWorker.renderPdfToCurrentView, Qt.QueuedConnection)
        self.rendererWorker.itemRenderFinished.connect(self.retrieveRenderedItem, Qt.QueuedConnection)
        self.rendererWorker.pdfRenderFinished.connect(self.rendererFinished)

        self.rendererWorker.absZoomFactor = self.rendererWorker.absZoomFactor

        self.rendererThread.start()

    @Slot(QPdfView, int, int)
    def retrieveRenderedItem(self, renderedItem, posX, posY):
        self.scene.addItem(renderedItem)
        renderedItem.setPos(posX, posY)
        renderedItem.setAsOrigin()


    @Slot()
    def rendererFinished(self):
        print("--- Loaded PDF within %s seconds ---" % (time.time() - self.start_time))

        # In case of a slow pc or a large pdf. Make sure to call that again
        t = QTimer()
        # t.singleShot(300, self.scrollTo)
        t.singleShot(500, self.pageGoto)
        t.singleShot(600, self.updateRenderedPages)


    def scrollTo(self):
        if self.gotoScrollPos != 0:
            self.verticalScrollBar().setMaximum(self.verticalScrollBar().maximumHeight())
            predictedScrollPos = self.gotoScrollPos
            self.verticalScrollBar().setValue(predictedScrollPos)
            self.update()
            self.gotoScrollPos = 0

            self.updateRenderedPages()

    def renderPdfToCurrentView(self, startPage=0):
        self.startPage = startPage
        self.renderPdf.emit(startPage)

    def updateRenderedPages(self, onlyPage=-1):
        '''
        Intended to be called repetitively on every ui change to redraw all visible pdf pages
        '''
        

        # Get all visible pages
        try:
            renderedItems = self.scene.items(self.mapToScene(self.viewport().geometry()))
        except Exception as identifier:
            print(str(identifier))
            return

        if onlyPage != -1:
            for renderedItem in renderedItems:
                if renderedItem.pageNumber == onlyPage:
                    self.rendererWorker.updatePage(renderedItem, zoom=self.rendererWorker.absZoomFactor, clip=self.viewport().geometry(), off=self.mapToScene(self.viewport().geometry()).boundingRect())
                    return

        hIdx = 1
        lIdx = len(self.rendererWorker.pages)

        # Iterate all visible items (shouldn't be that much normally)
        for renderedItem in renderedItems:
            # Check if we have a pdf view here (visible could be anything)
            if type(renderedItem) != QPdfView:
                continue

            if renderedItem.pageNumber > hIdx:
                hIdx = renderedItem.pageNumber
            if renderedItem.pageNumber < lIdx:
                lIdx = renderedItem.pageNumber

            self.rendererWorker.updatePage(renderedItem, zoom=self.rendererWorker.absZoomFactor, clip=self.viewport().geometry(), off=self.mapToScene(self.viewport().geometry()).boundingRect())

        for pIt in [lIdx-3,lIdx-2,lIdx-1,hIdx+1,hIdx+2,hIdx+3]:
            if pIt > -1 and pIt < len(self.rendererWorker.pages):
                if self.rendererWorker.pages[pIt].isDraft:
                    self.rendererWorker.updatePage(self.rendererWorker.pages[pIt], zoom=self.rendererWorker.absZoomFactor, clip=self.viewport().geometry(), off=self.mapToScene(self.viewport().geometry()).boundingRect())

                    self.rendererWorker.pages[pIt].isDraft = False


    def getPageSize(self, page=0):
        return self.rendererWorker.pdf.getPageSize(0)


    def viewportEvent(self, event):
        # if event.type() == QEvent.TouchBegin:
        #     event.accept()
        #     touchPointCount = len(event.touchPoints())

        #     if touchPointCount == 1:
        #         self.touching = event.touchPoints()[0].lastPos()

        if event.type() == QEvent.TouchUpdate or event.type() == QEvent.TouchBegin:
            touchPointCount = len(event.touchPoints())
            # print(touchPointCount)
            if touchPointCount == 2:
                # print('Two Finger touch')

                l1 = event.touchPoints()[0].startPos() - event.touchPoints()[1].startPos()
                l2 = event.touchPoints()[0].lastPos() - event.touchPoints()[1].lastPos()
                l3 = event.touchPoints()[0].lastPos() - event.touchPoints()[0].pos()

                distance = l1.manhattanLength() - l2.manhattanLength()

                zoomFactor = distance / 20000
                # Zoom
                if distance > 0 and self.rendererWorker.absZoomFactor > 0.4:
                    relZoomFactor = 1-zoomFactor
                elif distance < 0 and self.rendererWorker.absZoomFactor < 40:
                    relZoomFactor = 1/1-zoomFactor
                else:
                    relZoomFactor = 1

                self.rendererWorker.absZoomFactor = self.rendererWorker.absZoomFactor * relZoomFactor
                self.scale(relZoomFactor, relZoomFactor)

                self.updateIndicator = True

        if History.recentChanges == 1:
            self.changesMade.emit(True)
        elif History.recentChanges == 0:
            self.changesMade.emit(False)

        return super().viewportEvent(event)

    def wheelEvent(self, event):
        '''
        Overrides the default event
        '''
        self.rendererWorker.stopBackgroundRenderer()

        if not self.scene:
            return

        modifiers = QApplication.keyboardModifiers()

        Mmodo = QApplication.mouseButtons()
        if bool(Mmodo == Qt.RightButton) or bool(modifiers == Qt.ControlModifier):

            zoomInFactor = 1.05
            zoomOutFactor = 1 / zoomInFactor

            # Zoom
            if event.angleDelta().y() > 0:
                relZoomFactor = zoomInFactor
            else:
                relZoomFactor = zoomOutFactor

            self.rendererWorker.absZoomFactor = self.rendererWorker.absZoomFactor * relZoomFactor
            self.scale(relZoomFactor, relZoomFactor)

        else:
            super(GraphicsViewHandler, self).wheelEvent(event)

        self.updateRenderedPages()
        # self.updateIndicator = True
        # self.rendererWorker.enableBackgroundRenderer()


    # def mousePressEvent(self, event):
    #     '''
    #     Overrides the default event
    #     '''
    #     self.rendererWorker.stopBackgroundRenderer()

    #     super(GraphicsViewHandler, self).mousePressEvent(event)

    #     self.rendererWorker.enableBackgroundRenderer()


    def mouseReleaseEvent(self, event):
        '''
        Overrides the default event
        '''

        modifiers = QApplication.keyboardModifiers()

        Mmodo = QApplication.mouseButtons()
        if bool(modifiers == Qt.ControlModifier) and event.button() == Qt.RightButton:
            item = self.itemAt(event.pos())
            if type(item) == QPdfView:
                rect = self.mapToScene(self.viewport().geometry()).boundingRect()

                item.insertContent(event.pos(), self.rendererWorker.absZoomFactor, rect.x(), rect.y())

                self.updateRenderedPages()

        # self.rendererWorker.stopBackgroundRenderer()

        super(GraphicsViewHandler, self).mouseReleaseEvent(event)

        self.rendererWorker.enableBackgroundRenderer()


    def mouseMoveEvent(self, event):
        '''
        Overrides the default event
        '''
        self.rendererWorker.stopBackgroundRenderer()

        super(GraphicsViewHandler, self).mouseMoveEvent(event)

        if self.updateIndicator:
            self.updateRenderedPages()
            self.updateIndicator = False
        # if self.touching:
        #     distance = self.touching - event.pos()
        #     deltaX = int(distance.x())
        #     deltaY = int(distance.y())

        #     self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() + deltaX)
        #     self.verticalScrollBar().setValue(self.verticalScrollBar().value() + deltaY)

        #     self.touching = event.pos()

        self.rendererWorker.enableBackgroundRenderer()


    @Slot(QScroller.State)
    def scrollerStateChanged(self, newState):
        if newState == QScroller.Inactive:
            self.updateRenderedPages()


    def keyPressEvent(self, event):
        '''
        Overrides the default event
        '''
        # self.updateRenderedPages()
        self.rendererWorker.stopBackgroundRenderer()

        super(GraphicsViewHandler, self).keyPressEvent(event)

        self.rendererWorker.enableBackgroundRenderer()


    def keyReleaseEvent(self, event):
        '''
        Overrides the default event
        '''
        self.rendererWorker.stopBackgroundRenderer()

        self.updateRenderedPages()

        super(GraphicsViewHandler, self).keyReleaseEvent(event)

        self.rendererWorker.enableBackgroundRenderer()

    def tabletEvent(self, event):
        self.rendererWorker.stopBackgroundRenderer()

        item = self.itemAt(event.pos())
        if type(item) == QPdfView:


            # elif event.buttons() == Qt.LeftButton:


            # get the rectable of the current viewport
            rect = self.mapToScene(self.viewport().geometry()).boundingRect()
            # Store those properties for easy access
            item.tabletEvent(event.type(), event.pressure(), self.mapFromGlobalHighRes(event.pos(), event.globalPos(), event.hiResGlobalX(), event.hiResGlobalY()), self.rendererWorker.absZoomFactor, rect.x(), rect.y())

            if event.type() == QEvent.Type.TabletRelease:
                self.updateRenderedPages(item.pageNumber)
                item.RenderingFinished()

            #     if self.colorOverride:
            #         self.colorOverride = False

            #         Preferences.updateKeyValue('freehandColor', tuple(map(lambda x: str(x), (0,0,0))))


            # else:
            #     if event.buttons() == Qt.RightButton:
            #         self.colorOverride = True

            #         Preferences.updateKeyValue('freehandColor', tuple(map(lambda x: str(x), (1,0,0))))
                # elif 8 == int(event.buttons()):
                #     self.modeOverride = True

                #     item.editMode = editModes.eraser

        self.rendererWorker.enableBackgroundRenderer()


        return super(GraphicsViewHandler, self).tabletEvent(event)

    def mapFromGlobalHighRes(self, localPos, globalPos, globalHighResPosX, globalHighResPosY):
        # get high res global pos (floatPoint)
        highResGlobalQPos = QPointF(globalHighResPosX, globalHighResPosY)
        localPos = QPointF(localPos)
        globalPos = QPointF(globalPos)
        # the high res local pos is simply the difference between the global and the local pos.
        # e.g:                  100 + (200.12345         - 200)         = 100.12345
        highResLocalQPos = localPos + (highResGlobalQPos - globalPos)

        return highResLocalQPos

    def mapToItem(self, pos, item):
        '''
        Scene pos to item coordinates
        '''
        sRect = self.mapToScene(self.viewport().geometry()).boundingRect()
        # Store those properties for easy access
        viewportHeight = sRect.height()
        viewportWidth = sRect.width()
        viewportX = sRect.x()
        viewportY = sRect.y()

        newPos = QPoint(pos.x() + viewportX - item.x(), pos.y() - viewportY - item.y())

        return newPos

    def mapRectToItem(self, rect, item):
        '''
        Scene rect to item coordinates
        '''
        sRect = self.mapToScene(self.viewport().geometry()).boundingRect()
        # Store those properties for easy access
        viewportHeight = sRect.height()
        viewportWidth = sRect.width()
        viewportX = sRect.x()
        viewportY = sRect.y()

        newRect = QRectF(rect.topLef() + sRect - item, rect.y() - viewportY - item.y())

        return newRect

    def pageInsertHere(self):
        # Get all visible pages
        try:
            renderedItems = self.scene.items(self.mapToScene(self.viewport().geometry()))
        except Exception as e:
            return

        # Iterate all visible items (shouldn't be that much normally)
        for renderedItem in reversed(renderedItems):
            # Check if we have a pdf view here (visible could be anything)
            if type(renderedItem) != QPdfView:
                continue



            # Ok this needs to be reworked since there is to much overhead for just inserting a single page

            # fileName = self.saveCurrentPdf()
            # self.rendererWorker.pdf.closePdf()
            # os.replace(fileName, self.rendererWorker.pdf.filename)

            # prevScroll = self.verticalScrollBar().value()

            # self.setupScene()

            # self.loadPdfToCurrentView(self.rendererWorker.pdf.filename, renderedItem.pageNumber+2)

            x1, y1 = renderedItem.getEndPos()
            width, height = renderedItem.getSize()
            pIt = renderedItem.pageNumber+1

            # Insert after current page
            newPage = self.rendererWorker.pdf.insertPage(pIt)

            self.rendererWorker.loadPdfPageToCurrentView(pIt, 0, y1 + self.rendererWorker.DEFAULTPAGESPACE, self.rendererWorker.absZoomFactor)

            self.saveCurrentPdf(cleanup=False)

            items = self.scene.items()


            for item in items:
                if type(item) != QPdfView:
                    continue

                if item.pageNumber >= pIt:

                    item.pageNumber += 1
                    item.yOrigin = item.hOrigin + height + self.rendererWorker.DEFAULTPAGESPACE
                    item.setPos(item.x(), item.y() + (height+self.rendererWorker.DEFAULTPAGESPACE))

            return

    def pageExtendActive(self):
        # Get all visible pages
        try:
            renderedItems = self.scene.items(self.mapToScene(self.viewport().geometry()))
        except Exception as e:
            return

        # Iterate all visible items (shouldn't be that much normally)
        for renderedItem in reversed(renderedItems):
            # Check if we have a pdf view here (visible could be anything)
            if type(renderedItem) != QPdfView:
                continue

            renderedItem.page = self.rendererWorker.pdf.resizePage(renderedItem.page, 10, 10)


            # self.updateRenderedPages()

            # self.gotoScrollPos = prevScroll/

            return


    def pageDeleteActive(self):
        # Get all visible pages
        try:
            renderedItems = self.scene.items(self.mapToScene(self.viewport().geometry()))
        except Exception as e:
            return

        # Iterate all visible items (shouldn't be that much normally)
        for renderedItem in reversed(renderedItems):
            # Check if we have a pdf view here (visible could be anything)
            if type(renderedItem) != QPdfView:
                continue

            x1, y1 = renderedItem.getEndPos()
            width, height = renderedItem.getSize()
            pIt = renderedItem.pageNumber

            # Delete after current page
            if self.rendererWorker.pdf.deletePage(pIt):

                # fileName = self.saveCurrentPdf(cleanup=False)
                # self.rendererWorker.pdf.closePdf()
                # os.replace(fileName, self.rendererWorker.pdf.filename)

                # prevScroll = self.verticalScrollBar().value()

                # self.setupScene()

                # self.loadPdfToCurrentView(self.rendererWorker.pdf.filename, renderedItem.pageNumber+1)




                items = self.scene.items()

                for item in items:
                    if type(item) != QPdfView:
                        continue

                    if item.pageNumber > pIt:

                        item.pageNumber -= 1
                        item.yOrigin = item.hOrigin - height - self.rendererWorker.DEFAULTPAGESPACE
                        item.setPos(item.x(), item.y() - (height-self.rendererWorker.DEFAULTPAGESPACE))

                self.rendererWorker.removePdfPageFromCurrentView(renderedItem)

                self.scene.removeItem(renderedItem)

                self.saveCurrentPdf(cleanup=False)

                return True
            else:
                return False

    def getCurrentPageNumber(self):
        # Get all visible pages
        try:
            renderedItems = self.scene.items(self.mapToScene(self.viewport().geometry()))
        except Exception as e:
            return

        # Iterate all visible items (shouldn't be that much normally)
        for renderedItem in reversed(renderedItems):
            # Check if we have a pdf view here (visible could be anything)
            if type(renderedItem) != QPdfView:
                continue

            return renderedItem.pageNumber

    def pageGoto(self, pageNumber=-1):
        if self.rendererWorker.pages and pageNumber in range(len(self.rendererWorker.pages)):
            if pageNumber >= 1:
                predictedScrollPos = self.rendererWorker.pages[pageNumber - 1].yOrigin * self.rendererWorker.absZoomFactor
                self.verticalScrollBar().setValue(predictedScrollPos)
            else:
                self.verticalScrollBar().setValue(0)

            self.update()

            self.updateRenderedPages()

        else:
            if self.rendererWorker.pages and self.startPage in range(len(self.rendererWorker.pages)):
                self.pageGoto(self.startPage)
            else:
                print('No valid page entered')

    def pageFind(self, findStr):
        firstPage = -1

        for page in self.rendererWorker.pdf.doc:
            resultAreas = page.searchFor(findStr)
            if len(resultAreas) > 0:
                self.pageGoto(page.number+1)

    def zoomIn(self):
        zoomInFactor = 1.1

        self.rendererWorker.absZoomFactor = self.rendererWorker.absZoomFactor * zoomInFactor
        self.scale(zoomInFactor, zoomInFactor)

        self.updateRenderedPages()

    def zoomOut(self):
        zoomInFactor = 1.1
        zoomOutFactor = 1 / zoomInFactor

        self.rendererWorker.absZoomFactor = self.rendererWorker.absZoomFactor * zoomOutFactor
        self.scale(zoomOutFactor, zoomOutFactor)

        self.updateRenderedPages()

    def zoomToFit(self):
        pSize = self.getPageSize()

        rect = self.mapToScene(self.viewport().geometry()).boundingRect()
            # Store those properties for easy access

        ratio = rect.width() / pSize[0]

        self.rendererWorker.absZoomFactor = self.rendererWorker.absZoomFactor * ratio
        self.scale(ratio, ratio)

        self.updateRenderedPages()

    @Slot(int, int, int, bool, str)
    def toolBoxTextInputEvent(self, x, y, pageNumber, result, content):
        '''
        Triggered by the toolBox when user finished text editing
        '''
        # get the desired page which waits for user input
        self.rendererWorker.pages[pageNumber].textInputReceived(x, y, result, content)

        # Redraw all, as there are some changes now
        self.updateRenderedPages()

    @Slot(int, int, int, str)
    def toolBoxTextInputRequestedEvent(self, x, y, pageNumber, currentContent):
        '''
        Triggered by the pdfView when user requests text editing
        '''
        # Call the class intern signal to forward this request to the toolbox
        self.requestTextInput.emit(x, y, pageNumber, currentContent)

    @Slot(str)
    def editModeChangeRequest(self, editModeUpdate):
        global editMode

        editMode = editModeUpdate

        if toBool(Preferences.data["radioButtonNoInteractionWhileEditing"]):
            if editMode == editModes.none:
                self.scroller.grabGesture(self.viewport(), self.scroller.TouchGesture)

            else:
                self.scroller.ungrabGesture(self.viewport())



    @Slot(int, int)
    def addIndicatorPoint(self, x, y):
        self.tempObj.append(QGraphicsEllipseItem(x,y,8,8))
        self.tempObj[-1].setBrush(QBrush(QColor(*rgb.fore), style = Qt.SolidPattern))
        self.scene.addItem(self.tempObj[-1])

    @Slot()
    def deleteLastIndicatorPoint(self):
        try:
            self.scene.removeItem(self.tempObj[-1])
            del self.tempObj[-1]
        except IndexError as ie:
            # Don't judge me, but this can happen
            pass
        except Exception as identifier:
            print(str(identifier()))

    @Slot()
    def updateSuggested(self):
        self.updateRenderedPages()

    @Slot()
    def settingsUpdateSuggested(self):
        self.settingsChanged.emit()