# ---------------------------------------------------------------
# -- CXP Test GUI Core File --
#
# Implements core functionality
#
# Author: Melvin Strobl
# ---------------------------------------------------------------

from PyQt5.QtWidgets import QSizePolicy, QFrame, QDialog, QGraphicsView, QGraphicsScene, QApplication, QGraphicsPixmapItem, QGesture, QGraphicsLineItem
from PyQt5.QtCore import Qt, QRectF, QEvent
from PyQt5.QtGui import QPixmap


from interfaces import IregCon, IcsrCtrl
from preferences import Preferences

from pdfEngine import pdfEngine
from imageHelper import imageHelper

import subprocess  # for running external cmds
import os

from indexed import IndexedOrderedDict

import fitz

class QPdfView(QGraphicsPixmapItem):
    def __init__(self):
        QGraphicsPixmapItem.__init__(self)

    def setQImage(self, qImg):
        self.qImg = qImg

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

        print(self.hOrigin)

    def setPage(self, page):
        self.page = page

    def reloadQImg(self, zoomFactor):
        mat = fitz.Matrix(zoomFactor, zoomFactor)
        self.pixImg.convertFromImage(self.qImg)

    def getVisibleRect(self):
        pass

    def insertText(self):
        pass




class GraphicsViewHandler(QGraphicsView):
    pages = IndexedOrderedDict()
    DEFAULTPAGESPACE = 20
    CONTINOUSVIEW = True

    absZoomFactor = float(1)

    def __init__(self, parent):
        '''Create the Viewport.

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

        self.setDragMode(self.ScrollHandDrag)

        # self.grabGesture(QGesture.gestureType(self))
        # self.resize(parent.size())

    def loadPdfToCurrentView(self, pdfFilePath):
        self.pdf.openPdf(pdfFilePath)

        self.scene = QGraphicsScene()
        self.setScene(self.scene)

        # Start at the top
        posX = float(0)
        posY = float(0)

        for pIt in range(self.pdf.doc.pageCount):
            # Load each page to a new position in the current view.
            posX, posY = self.loadPdfPageToCurrentView(pIt, posX, posY)

        self.qli = QGraphicsLineItem(0,0,0,100)
        self.scene.addItem(self.qli)

    def loadPdfPageToCurrentView(self, pageNumber, posX, posY):

        pdfView = QPdfView()
        pdfView.setPage(self.pdf.getPage(pageNumber))

        self.updatePdf(pdfView, pageNumber = pageNumber)


        self.pages[pageNumber] = pdfView

        self.scene.addItem(self.pages[pageNumber])
        self.pages[pageNumber].setPos(posX, posY)

        if self.CONTINOUSVIEW:
            newPosX = posX
            newPosY = posY + pdfView.boundingRect().height() + self.DEFAULTPAGESPACE
        else:
            newPosX = posX + pdfView.boundingRect().width() + self.DEFAULTPAGESPACE
            newPosY = posY

        pdfView.setAsOrigin()

        return newPosX, newPosY

    def updateRenderedPages(self):
        # h = float(self.size().height())
        # w = float(self.size().width())
        # x = float(0)
        # y = float(0)

        # rect = QRectF(x,y,w,h)
        # print(w, h)
        # print(self.scene.sceneRect())

        renderedItems = self.scene.items(self.mapToScene(self.viewport().geometry()))

        rect = self.mapToScene(self.viewport().geometry()).boundingRect()
        viewportHeight = rect.height()
        viewportWidth = rect.width()
        viewportX = rect.x()
        viewportY = rect.y()
        print("")


        for renderedItem in renderedItems:
            if type(renderedItem) == QGraphicsLineItem:
                continue

            clipX = 0
            clipY = 0

            if(renderedItem.xOrigin < viewportX):
                print(str(renderedItem.page) + "\tPagestart out of scope")

                clipX = viewportX - renderedItem.xOrigin

            if(renderedItem.yOrigin < viewportY):
                print(str(renderedItem.page) + "\tPagestart out of scope")

                clipY = viewportY - renderedItem.yOrigin


            if((renderedItem.xOrigin + renderedItem.wOrigin) - (viewportX + viewportWidth) > 0):
                print(str(renderedItem.page) + "\tPageend out of scope")
                # Start in scope, End not in scope
                if clipX == 0:
                    clipW = renderedItem.xOrigin - viewportWidth
                # Start not in scope, End not in scope
                else:
                    clipW = viewportWidth

            else:
                # Start in scope, End in scope
                if clipX == 0:
                    clipW =  renderedItem.wOrigin - renderedItem.xOrigin - viewportX
                # Start not in scope, End in scope
                else:
                    clipW = renderedItem.wOrigin

            if((renderedItem.yOrigin + renderedItem.hOrigin) - (viewportY + viewportHeight) > 0):
                print(str(renderedItem.page) + "\tPageend out of scope")
                # Start in scope, End not in scope
                if clipY == 0:
                    clipH = (viewportY + viewportHeight) - renderedItem.yOrigin
                # Start not in scope, End not in scope
                else:
                    clipH = viewportHeight

            else:
                # Start in scope, End in scope
                if clipY == 0:
                    clipH = renderedItem.hOrigin - renderedItem.yOrigin - viewportY
                # Start not in scope, End in scope
                else:
                    clipH = renderedItem.hOrigin - clipY


            clip = QRectF(clipX, clipY, clipW, clipH)

            self.updatePdf(renderedItem, zoom = self.absZoomFactor, clip = clip)

            if clipX != 0:
                renderedItem.setPos(viewportX, renderedItem.yOrigin)
            if clipY != 0:
                renderedItem.setPos(renderedItem.xOrigin, viewportY)

            if clipX == 0 and clipY == 0:
                renderedItem.setPos(renderedItem.xOrigin, renderedItem.yOrigin)



    def insertText(self):
        h = float(self.size().height())
        w = float(self.size().width())
        x = float(0)
        y = float(0)

        rect = QRectF(x,y,w,h)
        # print(w, h)
        # print(self.scene.sceneRect())

        renderedItems = self.scene.items(self.mapToScene(self.viewport().geometry()))

        self.pdf.insertText(renderedItems[0].page, "hi")

    def updatePdf(self, pdf, zoom=absZoomFactor, clip=None, pageNumber = None):
        mat = fitz.Matrix(zoom, zoom)

        fClip = None
        if clip:
            fClip = fitz.Rect(clip.x(), clip.y(), clip.x() + clip.width(), clip.y() + clip.width())
            # fClip = fitz.Rect(clip.x(), clip.y(), clip.x() + clip.width(), clip.y() + clip.width())

        pixmap = self.pdf.renderPixmap(pdf.page, mat = mat, clip = fClip)

        qImg = self.pdf.getQImage(pixmap)
        qImg.setDevicePixelRatio(zoom)
        qImg = self.imageHelper.applyTheme(qImg)

        if pageNumber:
            pdf.setPixMap(qImg, pageNumber)
        else:
            pdf.updatePixMap(qImg)

    def getCurrentScaleFactor(self):
        print(self.mapToScene(self.viewport().geometry()))
        print(self.sceneRect())

    def wheelEvent(self, event):
        """
        Zoom in or out of the view.
        """
        if not self.scene:
            return

        modifiers = QApplication.keyboardModifiers()

        Mmodo = QApplication.mouseButtons()
        if bool(Mmodo == Qt.RightButton) or bool(modifiers == Qt.ControlModifier):

            zoomInFactor = 1.2
            zoomOutFactor = 1 / zoomInFactor

            # Save the scene pos
            oldPos = self.mapToScene(event.pos())

            # Zoom
            if event.angleDelta().y() > 0:
                relZoomFactor = zoomInFactor
            else:
                relZoomFactor = zoomOutFactor

            self.absZoomFactor = self.absZoomFactor * relZoomFactor
            self.scale(relZoomFactor, relZoomFactor)

            # Get the new position
            newPos = self.mapToScene(event.pos())

            # Move scene to old position
            delta = newPos - oldPos
            # self.translate(delta.x(), delta.y())

        else:
            QGraphicsView.wheelEvent(self, event)

        self.updateRenderedPages()


    def gestureEvent(self, event):
        print('hi')