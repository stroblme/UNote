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

    def setPage(self, page):
        self.page = page

    def reloadQImg(self, zoomFactor):
        mat = fitz.Matrix(zoomFactor, zoomFactor)
        self.pixImg.convertFromImage(self.qImg)

    def getVisibleRect(self):
        pass

    def insertText(self, qpos):
        h = float(22)
        w = float(120)

        textRect = fitz.Rect(qpos.x(), qpos.y() - h/2, qpos.x() + w, qpos.y() + h/2)

        cyan  = (14/255,125/255,145/255)                                   # some colors
        black = (0,0,0)
        white = (1,1,1)
        """We use a Shape object (something like a canvas) tot output the text and
        the rectangles surounding it for demonstration.
        """

        shape = self.page.newShape()                            # create Shape
        shape.drawRect(textRect)                                 # draw rectangles
        shape.finish(width = 1, color = cyan, fill = white)
        # Now insert text in the rectangles. Font "Helvetica" will be used
        # by default. A return code rc < 0 indicates insufficient space (not checked here).
        rc = shape.insertTextbox(textRect, fontsize=18, buffer="hi", color = black, rotate=0)
        if rc < 0:
            print('not enough space')
        shape.commit()


    def mousePressEvent(self, event):
        QGraphicsPixmapItem.mousePressEvent(event)
        if event.button() == Qt.RightButton:
            self.insertText(event.pos())



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

        # self.setDragMode(self.ScrollHandDrag)

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
        try:
            renderedItems = self.scene.items(self.mapToScene(self.viewport().geometry()))
        except Exception as e:
            return

        rect = self.mapToScene(self.viewport().geometry()).boundingRect()
        viewportHeight = rect.height()
        viewportWidth = rect.width()
        viewportX = rect.x()
        viewportY = rect.y()


        for renderedItem in renderedItems:
            if type(renderedItem) == QGraphicsLineItem:
                continue

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




    def insertText(self):
        try:
            renderedItems = self.scene.items(self.mapToScene(self.viewport().geometry()))
        except Exception as e:
            return

        for renderedItem in renderedItems:
            if not renderedItem.isUnderMouse():
                continue
            qTextPoint = renderedItem.mapFromScene(self.mousePos)
            item = renderedItem
            break


        


    def updatePdf(self, pdf, zoom=absZoomFactor, clip=None, pageNumber = None):
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
        super(GraphicsViewHandler, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        super(GraphicsViewHandler, self).mouseReleaseEvent(event)
        self.updateRenderedPages()

    def mouseMoveEvent(self, event):
        self.mousePos = event.localPos()
        super(GraphicsViewHandler, self).mouseMoveEvent(event)
        # self.updateRenderedPages()



    def gestureEvent(self, event):
        print('hi')