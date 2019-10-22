# ---------------------------------------------------------------
# -- CXP Test GUI Core File --
#
# Implements core functionality
#
# Author: Melvin Strobl
# ---------------------------------------------------------------

from PySide2.QtWidgets import QSizePolicy, QFrame, QDialog, QGraphicsView, QGraphicsScene, QApplication, QGraphicsPixmapItem
from PySide2.QtCore import Qt, QRectF

from interfaces import IregCon, IcsrCtrl
from preferences import Preferences

from pdfEngine import pdfEngine
from imageHelper import imageHelper

import subprocess  # for running external cmds
import os

from indexed import IndexedOrderedDict

import copy

# class QPdfView(QGraphicsPixmapItem):
#     def __init__(self, parent):
#         QGraphicsPixmapItem.__init__(self, parent)

#         self.parent = parent

#     def setQImage(self, qImg):
#         self.qImg = qImg

#     def reloadQImg(self):
#         pass

class GraphicsViewHandler(QGraphicsView):
    pages = IndexedOrderedDict()
    DEFAULTPAGESPACE = 20
    CONTINOUSVIEW = True


    def __init__(self, parent):
        '''Create the Viewport.

        :param parent: Parent editor widget.
        '''
        QGraphicsView.__init__(self, parent)

        self.parent = parent
        self.scaleFactor = 1.0

        self.pdfEngine = pdfEngine()
        self.imageHelper = imageHelper()

        self.setMouseTracking(True)
        self.setTabletTracking(True)
        self.setFrameShape(QFrame.StyledPanel)
        self.setObjectName("graphicsView")

        # self.resize(parent.size())

    def loadPdfToCurrentView(self, pdfFilePath):
        self.pdfEngine.openPdf(pdfFilePath)

        self.scene = QGraphicsScene()
        self.setScene(self.scene)


        posX = float(0)
        posY = float(0)
        for pIt in range(self.pdfEngine.doc.pageCount):
            posX, posY = self.loadPdfPageToCurrentView(pIt, posX, posY)


    def loadPdfPageToCurrentView(self, pageNumber, posX, posY):

        qImg = self.pdfEngine.renderPage(pageNumber)
        qImgItem = self.imageHelper.createImageItem(qImg)
        # pdfView = QPdfView(qImgItem)

        self.pages[pageNumber] = qImgItem

        self.scene.addItem(self.pages[pageNumber])
        self.pages[pageNumber].setPos(posX, posY)

        if self.CONTINOUSVIEW:
            newPosX = posX
            newPosY = posY + qImgItem.boundingRect().height() + self.DEFAULTPAGESPACE
        else:
            newPosX = posX + qImgItem.boundingRect().width() + self.DEFAULTPAGESPACE
            newPosY = posY

        return newPosX, newPosY

    def getRenderedPages(self):
        h = float(self.size().height())
        w = float(self.size().width())
        x = float(0)
        y = float(0)

        rect = QRectF(x,y,w,h)
        # print(w, h)
        # print(self.scene.sceneRect())

        renderedItems = self.scene.items(self.mapToScene(self.viewport().geometry()))

        for renderedItem in renderedItems:
            renderedItem.reloadQImg()

        # print(renderedItems)
        print(renderedItems)


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
                zoomFactor = zoomInFactor
            else:
                zoomFactor = zoomOutFactor
            self.scale(zoomFactor, zoomFactor)

            # Get the new position
            newPos = self.mapToScene(event.pos())

            # Move scene to old position
            delta = newPos - oldPos
            self.translate(delta.x(), delta.y())

            self.getRenderedPages()
        else:
            QGraphicsView.wheelEvent(self, event)