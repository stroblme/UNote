from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QPixmap, QPainter, QPen, QBrush, QColor, QPolygon
from PyQt5.QtCore import pyqtSignal, QFile, QTextStream, pyqtSlot, QObject, QPoint, Qt, QRect, QSize
from PyQt5.QtWidgets import QDialog, QGraphicsView, QGraphicsScene, QWidget, QPushButton, QVBoxLayout, QTextEdit, QGridLayout

from indexed import IndexedOrderedDict

from math import sin, cos

OUTEROFFSET = 8
TEXTBOXOFFSETTOP = 10
TEXTBOXOFFSETBOTTOM = 30

OUTERLINEWIDTH = OUTEROFFSET
INNERLINEWIDTH = 4

BUTTONOFFSETTOP = 17
BUTTONOFFSETBOTTOM = 10

CIRCLE = 5760

# class ToolBoxButton(QPushButton):
#     def __init__(self, parent, start, length):
#         '''
#         Creates a ToolBoxButton instance as a arc

#         :param start: starting point of the arc
#         :param length: length of the arc
#         '''
#         self.setArc(start, length)
#         # print('1')
#         QPushButton.__init__(self, parent)

#     def setArc(self, start, length):
#         self.start = start
#         self.length = length

#     def paintEvent(self, event):
#         self.drawPiePiece(event)

#         QPushButton.paintEvent(self, event)


#     def drawPiePiece(self, event):
#         outerPieRect = self.rect()
#         outerPieRect.adjust(+INNEROFFSET,+INNEROFFSET,-INNEROFFSET,-INNEROFFSET)

#         shapePainter = QPainter(self)
#         shapePainter.setRenderHint(shapePainter.Antialiasing)
#         shapePainter.setPen(QPen(QColor(14,125,145),  BOTTOMLINEWIDTH, Qt.SolidLine))
#         shapePainter.drawPie(outerPieRect, self.start, self.length)

#         self.move(BOTTOMOFFSET*sin((self.start+self.length)*CIRCLE), BOTTOMOFFSET*cos((self.start+self.length)*CIRCLE))


#     def mousePressEvent(self, event):
#         QPushButton.mousePressEvent(self, event)

#     def mouseMoveEvent(self, event):
#         QPushButton.mouseMoveEvent(self, event)

#     def mouseReleaseEvent(self, event):
#         QPushButton.mouseReleaseEvent(self, event)

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
        outerRect.adjust(+TEXTBOXOFFSETTOP,+TEXTBOXOFFSETTOP,-TEXTBOXOFFSETTOP,-TEXTBOXOFFSETBOTTOM)

        outerButtonRect = self.rect()
        outerButtonRect.adjust(+BUTTONOFFSETTOP,+BUTTONOFFSETTOP,-BUTTONOFFSETTOP,-BUTTONOFFSETBOTTOM)

        topLeft = outerButtonRect.topLeft()
        topRight = outerButtonRect.topRight()
        bottomLeft = QPoint(topLeft.x(), topLeft.y()+160)
        bottomRight = QPoint(topRight.x(), topRight.y()+160)

        # We use a textEdit for making text boxes editable for user
        self.pTextEdit = QTextEdit(self)
        # Always enable line wrapping
        self.pTextEdit.setLineWrapMode(QTextEdit.WidgetWidth)
        self.pTextEdit.setAutoFormatting(QTextEdit.AutoAll)
        self.pTextEdit.setAcceptRichText(True)
        self.pTextEdit.setPlaceholderText("Text Box Content")

        # Forward keypressevents from the textEdit to the parent toolBoxWidget
        self.keyPressEvent = self.pTextEdit.keyPressEvent
        self.keyReleaseEvent = self.pTextEdit.keyReleaseEvent

        # We need a layout to add the textBox to the toolBoxWidget
        widgetLayout = QGridLayout(self)
        widgetLayout.addWidget(self.pTextEdit)
        self.pTextEdit.setGeometry(outerRect)

        buttonSize = QSize(60,30)

        self.textButton = QPushButton(self)
        self.textButton.setFixedSize(buttonSize)
        self.textButton.move(topRight)
        self.textButton.setText('T')

        self.highlightButton = QPushButton(self)
        self.highlightButton.setFixedSize(buttonSize)
        self.highlightButton.move(topLeft)
        self.highlightButton.setText('H')

        self.okButton = QPushButton(self)
        self.okButton.setFixedSize(buttonSize)
        self.okButton.move(bottomLeft)
        self.okButton.setText('Ok')

        self.cancelButton = QPushButton(self)
        self.cancelButton.setFixedSize(buttonSize)
        self.cancelButton.move(bottomRight)
        self.cancelButton.setText('Cancel')




        # Set Shortcuts for the buttons
        self.textButton.setShortcut("Ctrl+T")
        self.highlightButton.setShortcut("Ctrl+H")
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
        else:
            # Draw the toolBoxShape
            self.drawCircularShape(event)

        # Run the parent paint Event
        QWidget.paintEvent(self, event)

    def drawCircularShape(self, paintEvent):
        '''
        Draws the circular toolBox shape
        '''
        outerCircleRect = self.rect()
        outerCircleRect.adjust(+OUTEROFFSET,+OUTEROFFSET,-OUTEROFFSET,-OUTEROFFSET)

        topLeft = outerCircleRect.topLeft()
        topRight = outerCircleRect.topRight()
        bottomLeft = QPoint(topLeft.x(), topRight.y() + 100)
        bottomRight = QPoint(topRight.x(), topRight.y() + 100)

        shapePainter = QPainter(self)
        shapePainter.setRenderHint(shapePainter.Antialiasing)
        shapePainter.setPen(QPen(QColor(14,125,145),  OUTERLINEWIDTH, Qt.SolidLine))
        shapePainter.drawArc(outerCircleRect, CIRCLE/2, CIRCLE/2)
        shapePainter.setPen(QPen(QColor(14,125,145),  OUTERLINEWIDTH, Qt.SolidLine))
        shapePainter.drawLine(topLeft, bottomLeft)
        shapePainter.drawLine(topRight, bottomRight)

        self.pTextEdit.setEnabled(False)
        self.pTextEdit.setVisible(False)

        self.okButton.setVisible(False)
        self.cancelButton.setVisible(False)
        self.highlightButton.setVisible(True)
        self.textButton.setVisible(True)


    def drawRectShape(self, event):
        '''
        Draws a rectangle for the textEdit box
        '''

        outerRect = self.rect()
        outerRect.adjust(+TEXTBOXOFFSETTOP,+TEXTBOXOFFSETTOP,-TEXTBOXOFFSETTOP,-TEXTBOXOFFSETTOP)


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

        self.okButton.setVisible(True)
        self.cancelButton.setVisible(True)
        self.highlightButton.setVisible(False)
        self.textButton.setVisible(False)

    def insertCurrentContent(self, content):
        '''
        Used to append the provided content to the textEdit box

        :param content: Text which should be displayed in the textEdit
        '''
        if content != "":
            self.pTextEdit.setText(content)
        else:
            self.pTextEdit.setText("")

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

    # def mouseReleaseEvent(self, event):
    #     '''
    #     Overrides the default event
    #     '''
    #     if self.__mousePressPos is not None:
    #         moved = event.globalPos() - self.__mousePressPos
    #         if moved.manhattanLength() > 3:
    #             event.ignore()
    #             return

    #     QWidget.mouseReleaseEvent(self, event)


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
