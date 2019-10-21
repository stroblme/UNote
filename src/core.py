# ---------------------------------------------------------------
# -- CXP Test GUI Core File --
#
# Implements core functionality
#
# Author: Melvin Strobl
# ---------------------------------------------------------------

from PySide2.QtWidgets import QDialog, QGraphicsView, QGraphicsScene

from interfaces import IregCon, IcsrCtrl
from preferences import Preferences

from pdfEngine import pdfEngine
from imageHelper import imageHelper

import subprocess  # for running external cmds
import os

class GraphicsViewHandler():

    def __init__(self, uiInst):
        super().__init__()

        self.uiInst = uiInst

        self.pdfEngine = pdfEngine()
        self.imageHelper = imageHelper()

    def loadPdfToCurrentView(self, pdfFilePath):
        self.loadPdfPageToCurrentView(pdfFilePath, 1)


    def loadPdfPageToCurrentView(self, pdfFilePath, pageNumber):
        self.qimg = self.pdfEngine.renderPdf(pdfFilePath, pageNumber)
        self.pixImgItem = self.imageHelper.createImageItem(self.qimg)

        self.scene = QGraphicsScene()
        self.scene.addItem(self.pixImgItem)
        self.uiInst.graphicsView.setScene(self.scene)
