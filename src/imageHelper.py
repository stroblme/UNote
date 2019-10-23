from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QFileDialog, QWidget, QGraphicsPixmapItem
from PyQt5.QtGui import QPixmap, QImage, QColor

from preferences import Preferences

class imageHelper(QWidget):
    dark = False

    def __init__(self):
        super().__init__()

    def createImageItem(self, qimg, qPdfView):
        qimg = self.applyTheme(qimg)
        pixImg = QPixmap()
        pixImg.convertFromImage(qimg)
        qPdfView.setPixmap(pixImg)

        return pixImgItem

    def applyTheme(self, qimage):
        if bool(Preferences.data["radioButtonDarkTheme"]) == True:
            qimage.invertPixels()
            return qimage
        else:
            return qimage
