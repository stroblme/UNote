from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QPixmap, QPainter, QPen, QBrush, QColor, QPolygon
from PyQt5.QtCore import pyqtSignal, QFile, QTextStream, pyqtSlot, QObject, QPoint, Qt, QRect
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
        '''
        Creates a ToolBoxButton instance as a arc

        :param start: starting point of the arc
        :param length: length of the arc
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
        '''
        Creates the toolboxwidget as child of the window widget

        :param parent: Parent window widget.
        '''
        QWidget.__init__(self, parent)
        self.initUI()




    def initUI(self):
        '''
        Sets up major UI components
        '''

        # Create a rectengle from teh given outer dimensions
        outerRect = self.rect()
        # Shrink it for matiching textBox size
        outerRect.adjust(+TEXTBOXOFFSET,+TEXTBOXOFFSET,-TEXTBOXOFFSET,-TEXTBOXOFFSET)

        # We use a textEdit for making text boxes editable for user
        self.pTextEdit = QTextEdit(self)
        # Always enable line wrapping
        self.pTextEdit.setLineWrapMode(QTextEdit.WidgetWidth)
        self.pTextEdit.setAutoFormatting(QTextEdit.AutoAll)
        self.pTextEdit.setAcceptRichText(True)
        self.pTextEdit.setPlaceholderText("Text Box Content")
        self.pTextEdit.setGeometry(outerRect)

        # Forward keypressevents from the textEdit to the parent toolBoxWidget
        self.keyPressEvent = self.pTextEdit.keyPressEvent
        self.keyReleaseEvent = self.pTextEdit.keyReleaseEvent

        # We need a layout to add the textBox to the toolBoxWidget
        widgetLayout = QGridLayout(self)
        widgetLayout.addWidget(self.pTextEdit)

        self.textButton = ToolBoxButton(self, 0, self.numberOfButtons/1 * self.numberOfButtons/CIRCLE)

        self.highlightButton = ToolBoxButton(self, 1 * self.numberOfButtons/CIRCLE, 2 * self.numberOfButtons/CIRCLE)

        self.okButton = ToolBoxButton(self, 2 * self.numberOfButtons/CIRCLE, 3 * self.numberOfButtons/CIRCLE)

        self.cancelButton = ToolBoxButton(self, 3 * self.numberOfButtons/CIRCLE, CIRCLE)

        # Set Shortcuts for the buttons
        self.okButton.setShortcut("Ctrl+Return")
        self.cancelButton.setShortcut("Esc")

        # Connect Events for the buttons
        self.okButton.clicked.connect(self.handleOkButton)
        self.cancelButton.clicked.connect(self.handleCancelButton)

    def paintEvent(self, event):
        '''
        Overrides the default paint event to either draw a textBox or a toolBox
        '''
        if self.textBoxMode:
            # Draw the text box
            self.drawRectShape(event)
            # And hide the control elements
            self.setButtonVisibility(False)
        else:
            # Draw the toolBoxShape
            self.drawCircularShape(event)
            # And show all buttons
            self.setButtonVisibility(True)

        # Run the parent paint Event
        QWidget.paintEvent(self, event)

    def drawCircularShape(self, paintEvent):
        '''
        Draws the circular toolBox shape
        '''
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


    def drawRectShape(self, event):
        '''
        Draws a rectangle for the textEdit box
        '''

        outerRect = self.rect()
        outerRect.adjust(+OUTEROFFSET,+OUTEROFFSET,-OUTEROFFSET,-OUTEROFFSET)

        moveRect = QRect(0,0, 11,11)

        shapePainter = QPainter(self)
        shapePainter.setRenderHint(shapePainter.Antialiasing)
        shapePainter.setPen(QPen(QColor(14,125,145),  OUTERLINEWIDTH, Qt.SolidLine))
        shapePainter.drawRect(outerRect)
        shapePainter.setPen(QPen(QColor(14,125,145),  2, Qt.SolidLine))
        shapePainter.drawArc(moveRect, 0, CIRCLE)

        self.pTextEdit.setEnabled(True)
        self.pTextEdit.setVisible(True)

        self.pTextEdit.ensureCursorVisible()
        self.pTextEdit.setFocus()

    def insertCurrentContent(self, content):
        '''
        Used to append the provided content to the textEdit box

        :param content: Text which should be displayed in the textEdit
        '''
        if content != "":
            self.pTextEdit.setText(content)
        else:
            self.pTextEdit.setText("")


    def setButtonVisibility(self, state):
        '''
        Sets the button visibility state depending on the param

        :param state: Desired visibility state of the toolBox buttons
        '''
        self.textButton.setVisible(state)
        self.highlightButton.setVisible(state)

        self.okButton.move(self.height(), self.width())
        self.cancelButton.move(self.height(), self.width())

    def mousePressEvent(self, event):
        '''
        Overrides the default event
        '''
        self.__mousePressPos = None
        self.__mouseMovePos = None
        if event.button() == QtCore.Qt.LeftButton:
            self.__mousePressPos = event.globalPos()
            self.__mouseMovePos = event.globalPos()

        QWidget.mousePressEvent(self, event)

    def mouseMoveEvent(self, event):
        '''
        Overrides the default event
        '''
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
        '''
        Overrides the default event
        '''
        if self.__mousePressPos is not None:
            moved = event.globalPos() - self.__mousePressPos
            if moved.manhattanLength() > 3:
                event.ignore()
                return

        QWidget.mouseReleaseEvent(self, event)


    @pyqtSlot(int, int, int, str)
    def handleTextInputRequest(self, x, y, pageNumber, currentContent):
        '''
        Slot when toolBox receives a textInput request. This is the case, when the user wants to insert a new or edit an existing textBox
        '''
        # Switch in to text box mode and redraw Widget
        self.currentPageNumber = pageNumber
        self.insertCurrentContent(currentContent)
        self.currentX = x
        self.currentY = y
        self.textBoxMode = True
        self.repaint()

    def handleOkButton(self):
        '''
        This method handles all the stuff that neees to be done, when the user successfully finished textEditing
        '''
        if self.textBoxMode:
            self.textInputFinished.emit(self.currentX, self.currentY, self.currentPageNumber, True, self.pTextEdit.toPlainText())
            self.textBoxMode = False
            self.repaint()
            self.currentPageNumber = -1
            self.currentX = -1
            self.currentY = -1

    def handleCancelButton(self):
        '''
        This method handles all the stuff that neees to be done, when the user canceled textEditing
        '''
        if self.textBoxMode:
            self.textInputFinished.emit(self.currentX, self.currentY, self.currentPageNumber, False, self.pTextEdit.toPlainText())
            self.textBoxMode = False
            self.repaint()
            self.currentPageNumber = -1
            self.currentX = -1
            self.currentY = -1
