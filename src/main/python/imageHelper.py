from PySide2.QtWidgets import QWidget
from PySide2.QtGui import QPixmap, QImage

from preferences import Preferences
from util import toBool

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
        if toBool(Preferences.data["radioButtonDarkTheme"]) == True:
            qimage.invertPixels()
            return qimage
        else:
            return qimage
