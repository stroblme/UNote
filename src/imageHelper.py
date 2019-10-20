from PySide2 import QtWidgets, QtCore, QtGui
from PySide2.QtWidgets import QFileDialog, QWidget, QGraphicsPixmapItem
from PySide2.QtGui import QPixmap, QImage, QColor

from preferences import Preferences

class imageHelper(QWidget):
    dark = False

    def __init__(self):
        super().__init__()

    def createImageItem(self, qimg):
        qimg = self.applyTheme(qimg)
        pixImg = QPixmap()
        pixImg.convertFromImage(qimg)
        pixImgItem = QGraphicsPixmapItem()
        pixImgItem.setPixmap(pixImg)

        return pixImgItem

    def applyTheme(self, qimage):
        if bool(Preferences.data["radioButtonDarkTheme"]) == True:
            qimage.invertPixels()
            return qimage
        else:
            return qimage
