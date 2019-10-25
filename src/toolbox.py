from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QPixmap, QPainter, QPen, QBrush, QColor, QPolygon
from PyQt5.QtCore import pyqtSignal, QFile, QTextStream, pyqtSlot, QObject, QPoint, Qt
from PyQt5.QtWidgets import QDialog, QGraphicsView, QGraphicsScene, QWidget, QPushButton, QVBoxLayout

from indexed import IndexedOrderedDict

INNEROFFSET = 80
OUTEROFFSET = 8

OUTERLINEWIDTH = OUTEROFFSET
INNERLINEWIDTH = 4

BOTTOMLINEWIDTH = 2

class ToolBoxItems():
    numberOfButtons = 2

    textButtonName = 'textButton'
    highlightButtonName = 'highlightButton'

    self.items = IndexedOrderedDict()

    def __init__(self, parent):
        super().__init__()

    def loadButtons(self, ):
        textButton = ToolBoxButton(parent)
        highlightButton = ToolBoxButton(parent)

        self.items[self.textButtonName] = textButton
        self.items[self.highlightButtonName] = highlightButton

class ToolBoxButton(QPushButton):
    def __init__(self, parent):
        '''Create the Viewport.

        :param parent: Parent editor widget.
        '''
        QPushButton.__init__(self, parent)

    def setArc(self, start, length):
        self.start = start
        self.length = length

    def paintEvent(self, event):
        self.drawPiePiece(event)

    def drawPiePiece(self, event):
        outerPieRect = self.rect()
        outerPieRect.adjust(+INNEROFFSET,+INNEROFFSET,-INNEROFFSET,-INNEROFFSET)

        shapePainter = QPainter(self)
        shapePainter.setRenderHint(shapePainter.Antialiasing)
        shapePainter.setPen(QPen(QColor(14,125,145),  BOTTOMLINEWIDTH, Qt.SolidLine))
        shapePainter.drawPie(outerPieRect, self.start, self.length)

    def mousePressEvent(self, event):
        QPushButton.mousePressEvent(self, event)

    def mouseMoveEvent(self, event):
        QPushButton.mouseMoveEvent(self, event)

    def mouseReleaseEvent(self, event):
        QPushButton.mouseReleaseEvent(self, event)

class ToolBoxWidget(QWidget):


    def __init__(self, parent):
        '''Create the Viewport.

        :param parent: Parent editor widget.
        '''
        QWidget.__init__(self, parent)


    def paintEvent(self, event):
        self.drawCircularShape(event)
        self.drawButtons(event)

    def drawCircularShape(self, paintEvent):
        outerCircleRect = self.rect()
        outerCircleRect.adjust(+OUTEROFFSET,+OUTEROFFSET,-OUTEROFFSET,-OUTEROFFSET)

        innerCircleRect = self.rect()
        innerCircleRect.adjust(+INNEROFFSET,+INNEROFFSET,-INNEROFFSET,-INNEROFFSET)

        shapePainter = QPainter(self)
        shapePainter.setRenderHint(shapePainter.Antialiasing)
        shapePainter.setPen(QPen(QColor(14,125,145),  OUTERLINEWIDTH, Qt.SolidLine))
        shapePainter.drawArc(outerCircleRect, 0, 5760)
        shapePainter.setPen(QPen(QColor(14,125,145),  INNERLINEWIDTH, Qt.SolidLine))
        shapePainter.drawArc(innerCircleRect, 0, 5760)

    def drawButtons(self, event):
        self.toolBoxItems = ToolBoxItems(self)

        arcStart = 0
        arcLength = 5760/self.toolBoxItems.numberOfButtons

        for toolBoxItem in self.toolBoxItems.items:
            toolBoxItem.

    def mousePressEvent(self, event):
        self.__mousePressPos = None
        self.__mouseMovePos = None
        if event.button() == QtCore.Qt.LeftButton:
            self.__mousePressPos = event.globalPos()
            self.__mouseMovePos = event.globalPos()

        QWidget.mousePressEvent(self, event)

    def mouseMoveEvent(self, event):
        if event.buttons() == QtCore.Qt.LeftButton:
            # adjust offset from clicked point to origin of widget
            currPos = self.mapToGlobal(self.pos())
            globalPos = event.globalPos()
            diff = globalPos - self.__mouseMovePos
            newPos = self.mapFromGlobal(currPos + diff)
            self.move(newPos)

            self.__mouseMovePos = globalPos

        QWidget.mouseMoveEvent(self, event)

    def mouseReleaseEvent(self, event):
        if self.__mousePressPos is not None:
            moved = event.globalPos() - self.__mousePressPos
            if moved.manhattanLength() > 3:
                event.ignore()
                return

        QWidget.mouseReleaseEvent(self, event)