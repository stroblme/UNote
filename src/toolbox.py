from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QPixmap, QPainter, QPen, QBrush, QColor, QPolygon
from PyQt5.QtCore import pyqtSignal, QFile, QTextStream, pyqtSlot, QObject, QPoint, Qt
from PyQt5.QtWidgets import QDialog, QGraphicsView, QGraphicsScene, QWidget, QPushButton, QVBoxLayout


class ToolBoxWidget(QWidget):

    def __init__(self, parent):
        '''Create the Viewport.

        :param parent: Parent editor widget.
        '''
        QWidget.__init__(self, parent)

    def paintEvent(self, event):
        self.drawCircularShape(event)

    def drawCircularShape(self, paintEvent):
        circleRect = self.rect()
        circleRect.adjust(+10,+10,-10,-10)
        painter = QPainter(self)
        painter.setRenderHint(painter.Antialiasing)
        painter.setPen(QPen(QColor(14,125,145),  8, Qt.SolidLine))
        painter.drawArc(circleRect, 0, 5760)
        
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