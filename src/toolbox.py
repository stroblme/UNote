from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QPixmap, QPainter, QPen, QBrush, QColor, QPolygon
from PyQt5.QtCore import pyqtSignal, QFile, QTextStream, pyqtSlot, QObject, QPoint, Qt
from PyQt5.QtWidgets import QDialog, QGraphicsView, QGraphicsScene, QWidget, QPushButton, QVBoxLayout

from indexed import IndexedOrderedDict

from math import sin, cos

INNEROFFSET = 80
OUTEROFFSET = 8

OUTERLINEWIDTH = OUTEROFFSET
INNERLINEWIDTH = 4

BOTTOMLINEWIDTH = 2
BOTTOMOFFSET = 20

CIRCLE = 5760

class ToolBoxButton(QPushButton):
    def __init__(self, parent, start, length):
        '''Create the Viewport.

        :param parent: Parent editor widget.
        '''
        self.setArc(start, length)
        # print('1')
        QPushButton.__init__(self, parent)

    def setArc(self, start, length):
        self.start = start
        self.length = length

    def paintEvent(self, event):
        self.drawPiePiece(event)

        QPushButton.paintEvent(self, event)


    def drawPiePiece(self, event):
        outerPieRect = self.rect()
        outerPieRect.adjust(+INNEROFFSET,+INNEROFFSET,-INNEROFFSET,-INNEROFFSET)

        shapePainter = QPainter(self)
        shapePainter.setRenderHint(shapePainter.Antialiasing)
        shapePainter.setPen(QPen(QColor(14,125,145),  BOTTOMLINEWIDTH, Qt.SolidLine))
        shapePainter.drawPie(outerPieRect, self.start, self.length)

        self.move(BOTTOMOFFSET*sin((self.start+self.length)/CIRCLE), BOTTOMOFFSET*cos((self.start+self.length)/CIRCLE))


    def mousePressEvent(self, event):
        QPushButton.mousePressEvent(self, event)

    def mouseMoveEvent(self, event):
        QPushButton.mouseMoveEvent(self, event)

    def mouseReleaseEvent(self, event):
        QPushButton.mouseReleaseEvent(self, event)

class ToolBoxWidget(QWidget):
    numberOfButtons = 2

    textButtonName = 'textButton'
    highlightButtonName = 'highlightButton'

    textBoxMode = False

    items = IndexedOrderedDict()

    def __init__(self, parent):
        '''Create the Viewport.

        :param parent: Parent editor widget.
        '''
        QWidget.__init__(self, parent)
        self.drawButtons()

    def paintEvent(self, event):
        if self.textBoxMode:
            self.drawRectShape(event)
        else:
            self.drawCircularShape(event)

        QWidget.paintEvent(self, event)

    def drawCircularShape(self, paintEvent):
        outerCircleRect = self.rect()
        outerCircleRect.adjust(+OUTEROFFSET,+OUTEROFFSET,-OUTEROFFSET,-OUTEROFFSET)

        innerCircleRect = self.rect()
        innerCircleRect.adjust(+INNEROFFSET,+INNEROFFSET,-INNEROFFSET,-INNEROFFSET)

        shapePainter = QPainter(self)
        shapePainter.setRenderHint(shapePainter.Antialiasing)
        shapePainter.setPen(QPen(QColor(14,125,145),  OUTERLINEWIDTH, Qt.SolidLine))
        shapePainter.drawArc(outerCircleRect, 0, CIRCLE)
        shapePainter.setPen(QPen(QColor(14,125,145),  INNERLINEWIDTH, Qt.SolidLine))
        shapePainter.drawArc(innerCircleRect, 0, CIRCLE)

    def drawRectShape(self, event):
        outerRect = self.rect()
        outerRect.adjust(+OUTEROFFSET,+OUTEROFFSET,-OUTEROFFSET,-OUTEROFFSET)

        shapePainter = QPainter(self)
        shapePainter.setRenderHint(shapePainter.Antialiasing)
        shapePainter.setPen(QPen(QColor(14,125,145),  OUTERLINEWIDTH, Qt.SolidLine))
        shapePainter.drawRect(outerRect)


    def drawButtons(self):
        self.textButton = ToolBoxButton(self, 0, CIRCLE/self.numberOfButtons)

        self.highlightButton = ToolBoxButton(self, 1 * CIRCLE/self.numberOfButtons, CIRCLE)
        pass

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