# ---------------------------------------------------------------
# -- CXP Test GUI Core File --
#
# Implements core functionality
#
# Author: Melvin Strobl
# ---------------------------------------------------------------

from PySide2.QtWidgets import QSizePolicy, QFrame, QDialog, QGraphicsView, QGraphicsScene

from interfaces import IregCon, IcsrCtrl
from preferences import Preferences

from pdfEngine import pdfEngine
from imageHelper import imageHelper

import subprocess  # for running external cmds
import os

from indexed import IndexedOrderedDict

import copy


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

        qimg = self.pdfEngine.renderPage(pageNumber)

        pixImgItem = self.imageHelper.createImageItem(qimg)

        self.pages[pageNumber] = qimg, pixImgItem

        self.scene.addItem(self.pages[pageNumber][1])
        self.pages[pageNumber][1].setPos(posX, posY)

        if self.CONTINOUSVIEW:
            newPosX = posX
            newPosY = posY + pixImgItem.boundingRect().height() + self.DEFAULTPAGESPACE
        else:
            newPosX = posX + pixImgItem.boundingRect().width() + self.DEFAULTPAGESPACE
            newPosY = posY

        return newPosX, newPosY
