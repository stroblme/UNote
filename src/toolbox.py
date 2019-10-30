from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QPixmap, QPainter, QPen, QBrush, QColor, QPolygon
from PyQt5.QtCore import pyqtSignal, QFile, QTextStream, pyqtSlot, QObject, QPoint, Qt
from PyQt5.QtWidgets import QDialog, QGraphicsView, QGraphicsScene, QWidget, QPushButton, QVBoxLayout, QTextEdit, QGridLayout

from indexed import IndexedOrderedDict

from math import sin, cos

INNEROFFSET = 80
OUTEROFFSET = 8
TEXTBOXOFFSET = 10

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

        self.move(BOTTOMOFFSET*sin((self.start+self.length)*CIRCLE), BOTTOMOFFSET*cos((self.start+self.length)*CIRCLE))


    def mousePressEvent(self, event):
        QPushButton.mousePressEvent(self, event)

    def mouseMoveEvent(self, event):
        QPushButton.mouseMoveEvent(self, event)

    def mouseReleaseEvent(self, event):
        QPushButton.mouseReleaseEvent(self, event)

class ToolBoxWidget(QWidget):
    numberOfButtons = 4

    textButtonName = 'textButton'
    highlightButtonName = 'highlightButton'
    okButtonName = 'okButton'
    cancelButtonName = 'cancelButton'

    textBoxMode = False

    items = IndexedOrderedDict()

    textInputFinished = pyqtSignal(int, int, int, bool, str)
    currentPageNumber = -1
    currentX = -1
    currentY = -1

    def __init__(self, parent):
        '''Create the Viewport.

        :param parent: Parent editor widget.
        '''
        QWidget.__init__(self, parent)
        self.initUI()


    def paintEvent(self, event):
        if self.textBoxMode:
            self.drawRectShape(event)
            self.setButtonVisibility(False)
        else:
            self.drawCircularShape(event)
            self.setButtonVisibility(True)

        QWidget.paintEvent(self, event)

    def initUI(self):
        outerRect = self.rect()
        outerRect.adjust(+TEXTBOXOFFSET,+TEXTBOXOFFSET,-TEXTBOXOFFSET,-TEXTBOXOFFSET)
        self.pTextEdit = QTextEdit(self)
        self.pTextEdit.setLineWrapMode(QTextEdit.WidgetWidth)
        self.pTextEdit.setAutoFormatting(QTextEdit.AutoAll)
        self.pTextEdit.setAcceptRichText(True)
        self.pTextEdit.setPlaceholderText("Text Box Content")
        self.pTextEdit.setGeometry(outerRect)

        self.keyPressEvent = self.pTextEdit.keyPressEvent
        self.keyReleaseEvent = self.pTextEdit.keyReleaseEvent

        widgetLayout = QGridLayout(self)
        widgetLayout.addWidget(self.pTextEdit)

        self.textButton = ToolBoxButton(self, 0, self.numberOfButtons/1 * self.numberOfButtons/CIRCLE)

        self.highlightButton = ToolBoxButton(self, 1 * self.numberOfButtons/CIRCLE, 2 * self.numberOfButtons/CIRCLE)

        self.okButton = ToolBoxButton(self, 2 * self.numberOfButtons/CIRCLE, 3 * self.numberOfButtons/CIRCLE)

        self.cancelButton = ToolBoxButton(self, 3 * self.numberOfButtons/CIRCLE, CIRCLE)

        self.okButton.setShortcut("Ctrl+Return")
        self.cancelButton.setShortcut("Esc")

        self.okButton.clicked.connect(self.handleOkButton)
        self.cancelButton.clicked.connect(self.handleCancelButton)

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

        self.pTextEdit.setEnabled(False)
        self.pTextEdit.setVisible(False)
        self.pTextEdit.setText("")

    def drawRectShape(self, event):
        outerRect = self.rect()
        outerRect.adjust(+OUTEROFFSET,+OUTEROFFSET,-OUTEROFFSET,-OUTEROFFSET)

        shapePainter = QPainter(self)
        shapePainter.setRenderHint(shapePainter.Antialiasing)
        shapePainter.setPen(QPen(QColor(14,125,145),  OUTERLINEWIDTH, Qt.SolidLine))
        shapePainter.drawRect(outerRect)

        self.pTextEdit.ensureCursorVisible()

        self.pTextEdit.setEnabled(True)
        self.pTextEdit.setVisible(True)

    def setButtonVisibility(self, state):
        self.textButton.setVisible(state)
        self.highlightButton.setVisible(state)

        self.okButton.move(self.height(), self.width())
        self.cancelButton.move(self.height(), self.width())

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


    @pyqtSlot(int, int, int)
    def handleTextInputRequest(self, x, y, pageNumber):
        # Switch in to text box mode and redraw Widget
        self.currentPageNumber = pageNumber
        self.currentX = x
        self.currentY = y
        self.textBoxMode = True
        self.repaint()

    def handleOkButton(self):
        print('ok')
        if self.textBoxMode:
            self.textInputFinished.emit(self.currentX, self.currentY, self.currentPageNumber, True, self.pTextEdit.toPlainText())
            self.textBoxMode = False
            self.repaint()
            self.currentPageNumber = -1



    def handleCancelButton(self):
        print('cancel')

        if self.textBoxMode:
            self.textInputFinished.emit(self.currentX, self.currentY, self.currentPageNumber, False, self.pTextEdit.toPlainText())
            self.textBoxMode = False
            self.repaint()
            self.currentPageNumber = -1
