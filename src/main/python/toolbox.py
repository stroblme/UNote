from math import sin, cos
from indexed import IndexedOrderedDict

from PyQt5.QtGui import QPainter, QPen, QColor, QIcon
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QPoint, Qt, QRect, QSize
from PyQt5.QtWidgets import QWidget, QPushButton, QTextEdit, QGridLayout, QSlider

import colorsys

import assets

from editHelper import editModes
from preferences import Preferences
from historyHandler import History

OUTEROFFSETTOP = 25
OUTEROFFSETBOTTOM = 14

TEXTBOXOFFSETTOP = 5
TEXTBOXOFFSETBOTTOM = 30

OUTERLINEWIDTH = OUTEROFFSETBOTTOM
INNERLINEWIDTH = 4

BUTTONOFFSETTOP = 17
BUTTONOFFSETBOTTOM = 15

CIRCLE = 5760


class ToolBoxWidget(QWidget):
    '''
    Class which creates a toolbox storing all available tools and handles text input
    '''
    numberOfButtons = 4

    textButtonName = 'textButton'
    markerButtonName = 'markerButton'
    okButtonName = 'okButton'
    cancelButtonName = 'cancelButton'

    items = IndexedOrderedDict()

    textInputFinished = pyqtSignal(int, int, int, bool, str)
    currentPageNumber = -1
    currentX = -1
    currentY = -1

    editMode = editModes.none

    editModeChange = pyqtSignal(str)

    suggestUpdate = pyqtSignal()

    editTextBox = False

    buttons = IndexedOrderedDict()

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
        textBoxRect = self.rect()
        # Shrink it for matiching textBox size
        textBoxRect.adjust(+30,+30,-12,-12)

        buttonRect = self.rect()
        buttonRect.adjust(+29,+30,+15,-20)

        self.row1Left = buttonRect.topLeft()
        self.row1Right = buttonRect.topRight()
        self.row2Left = QPoint(self.row1Left.x(), self.row1Left.y()+35)
        self.row2Right = QPoint(self.row1Right.x(), self.row1Right.y()+35)
        self.row3Left = QPoint(self.row2Left.x(), self.row2Left.y()+35)
        self.row3Right = QPoint(self.row2Right.x(), self.row2Right.y()+35)
        self.bottomLeft = QPoint(buttonRect.topLeft().x(), buttonRect.topLeft().y()+140)
        self.bottomRight = QPoint(self.row1Right.x(), self.row1Right.y()+140)
        self.bottomMiddle = QPoint(self.row1Left.x()+65, self.row1Right.y())

        # We use a textEdit for making text boxes editable for user
        self.pTextEdit = QTextEdit(self)
        # Always enable line wrapping
        self.pTextEdit.setLineWrapMode(QTextEdit.WidgetWidth)
        self.pTextEdit.setAutoFormatting(QTextEdit.AutoAll)
        self.pTextEdit.setAcceptRichText(True)
        self.pTextEdit.setFontPointSize(10)
        self.pTextEdit.setPlaceholderText("Text Box Content")

        # Forward keypressevents from the textEdit to the parent toolBoxWidget
        self.keyPressEvent = self.pTextEdit.keyPressEvent
        self.keyReleaseEvent = self.pTextEdit.keyReleaseEvent

        # We need a layout to add the textBox to the toolBoxWidget
        widgetLayout = QGridLayout(self)
        widgetLayout.addWidget(self.pTextEdit)
        self.pTextEdit.setGeometry(textBoxRect)

        buttonSize = QSize(60,30)

        # -----------------------------
        # Toolbuttons
        # -----------------------------

        self.textButton = QPushButton(self)
        self.textButton.setFixedSize(buttonSize)
        self.textButton.move(self.row1Right)
        self.textButton.setIcon(QIcon(":/assets/text.png"))
        self.textButton.setCheckable(True)
        self.buttons['textButton'] = self.textButton

        self.markerButton = QPushButton(self)
        self.markerButton.setFixedSize(buttonSize)
        self.markerButton.move(self.row1Left)
        self.markerButton.setIcon(QIcon(":/assets/marker.png"))
        self.markerButton.setCheckable(True)
        self.buttons['markerButton'] = self.markerButton

        self.freehandButton = QPushButton(self)
        self.freehandButton.setFixedSize(buttonSize)
        self.freehandButton.move(self.row2Left)
        self.freehandButton.setIcon(QIcon(":/assets/freehand.png"))
        self.freehandButton.setCheckable(True)
        self.buttons['freehandButton'] = self.freehandButton

        self.markdownButton = QPushButton(self)
        self.markdownButton.setFixedSize(buttonSize)
        self.markdownButton.move(self.row2Right)
        self.markdownButton.setIcon(QIcon(":/assets/markdown.png"))
        self.markdownButton.setCheckable(True)
        self.buttons['markdownButton'] = self.markdownButton

        self.formsButton = QPushButton(self)
        self.formsButton.setFixedSize(buttonSize)
        self.formsButton.move(self.row3Left)
        self.formsButton.setIcon(QIcon(":/assets/forms.png"))
        self.formsButton.setCheckable(True)
        self.buttons['formsButton'] = self.formsButton

        self.eraserButton = QPushButton(self)
        self.eraserButton.setFixedSize(buttonSize)
        self.eraserButton.move(self.row3Right)
        self.eraserButton.setIcon(QIcon(":/assets/eraser.png"))
        self.eraserButton.setCheckable(True)
        self.buttons['eraserButton'] = self.eraserButton

        self.okButton = QPushButton(self)
        self.okButton.setFixedSize(buttonSize)
        self.okButton.move(self.bottomLeft)
        self.okButton.setIcon(QIcon(":/assets/ok.png"))
        self.buttons['okButton'] = self.okButton

        self.cancelButton = QPushButton(self)
        self.cancelButton.setFixedSize(buttonSize)
        self.cancelButton.move(self.bottomRight)
        self.cancelButton.setIcon(QIcon(":/assets/cancel.png"))
        self.buttons['cancelButton'] = self.cancelButton

        self.deleteButton = QPushButton(self)
        self.deleteButton.setFixedSize(buttonSize)
        self.deleteButton.move(self.bottomRight)
        self.deleteButton.setIcon(QIcon(":/assets/delete.png"))
        self.buttons['deleteButton'] = self.deleteButton

        self.undoButton = QPushButton(self)
        self.undoButton.setFixedSize(buttonSize)
        self.undoButton.move(self.bottomLeft)
        self.undoButton.setIcon(QIcon(":/assets/undo.png"))
        self.buttons['undoButton'] = self.undoButton

        self.redoButton = QPushButton(self)
        self.redoButton.setFixedSize(buttonSize)
        self.redoButton.move(self.bottomRight)
        self.redoButton.setIcon(QIcon(":/assets/redo.png"))
        self.buttons['redoButton'] = self.redoButton

        # -----------------------------
        # Preference Buttons
        # -----------------------------

        self.sizeButton = QPushButton(self)
        self.sizeButton.setFixedSize(buttonSize)
        self.sizeButton.setIcon(QIcon(":/assets/size.png"))
        self.sizeButton.setCheckable(True)
        self.buttons['sizeButton'] = self.sizeButton


        self.colorButton = QPushButton(self)
        self.colorButton.setFixedSize(buttonSize)
        self.colorButton.setIcon(QIcon(":/assets/color.png"))
        self.colorButton.setCheckable(True)
        self.buttons['colorButton'] = self.colorButton


        # Set Shortcuts for the buttons
        self.textButton.setShortcut("Ctrl+T")
        self.markerButton.setShortcut("Ctrl+M")
        self.freehandButton.setShortcut("Ctrl+D")
        self.eraserButton.setShortcut("Ctrl+E")
        self.okButton.setShortcut("Ctrl+Return")
        self.cancelButton.setShortcut("Esc")
        self.deleteButton.setShortcut("Ctrl+Del")
        self.undoButton.setShortcut("Ctrl+Z")
        self.redoButton.setShortcut("Ctrl+Y")
        self.sizeButton.setShortcut("Ctrl+X")
        self.colorButton.setShortcut("Ctrl+L")

        # Connect Events for the buttons
        self.okButton.clicked.connect(self.handleOkButton)
        self.markerButton.clicked.connect(self.handleMarkerButton)
        self.textButton.clicked.connect(self.handleTextButton)
        self.formsButton.clicked.connect(self.handleFormsButton)
        self.freehandButton.clicked.connect(self.handleFreehandButton)
        self.eraserButton.clicked.connect(self.handleEraserButton)
        self.markdownButton.clicked.connect(self.handleMarkdownButton)
        self.cancelButton.clicked.connect(self.handleCancelButton)
        self.deleteButton.clicked.connect(self.handleDeleteButton)
        self.undoButton.clicked.connect(self.handleUndoButton)
        self.redoButton.clicked.connect(self.handleRedoButton)
        self.sizeButton.clicked.connect(self.handleSizeButton)
        self.colorButton.clicked.connect(self.handleColorButton)

        sliderSize = QSize(15,140)

        self.slider = QSlider(Qt.Vertical, self)
        self.slider.setMinimum(50)
        self.slider.setMaximum(150)
        self.slider.setValue(100)
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.setTickInterval(10)
        self.slider.move(self.bottomMiddle)
        self.slider.setFixedSize(sliderSize)
        self.slider.setEnabled(False)
        self.slider.valueChanged.connect(self.handleSliderValueChange)
        self.slider.sliderReleased.connect(self.handleSliderValueChanged)

        self.setButtonState()



    def restoreDefaults(self):
        '''
        Restores defaults for certain edit components
        '''

        black = (0,0,0)
        yellow = (1,1,0)

        # restore defaults for better ux
        Preferences.updateKeyValue('freehandColor', tuple(map(lambda x: str(x), black)))
        Preferences.updateKeyValue('markerColor', tuple(map(lambda x: str(x), yellow)))


    def paintEvent(self, event):
        '''
        Overrides the default paint event to either draw a textBox or a toolBox
        '''
        if self.editTextBox:
            # Draw the toolBoxShape
            self.drawRectShape(event)
        else:
            self.drawToolBoxShape(event)

        # Run the parent paint Event
        return QWidget.paintEvent(self, event)

    def drawToolBoxShape(self, paintEvent):
        '''
        Draws the circular toolBox shape
        '''
        outerCircleRect = self.rect()
        outerCircleRect.adjust(+OUTEROFFSETBOTTOM,+OUTEROFFSETTOP,-OUTEROFFSETBOTTOM,-OUTEROFFSETBOTTOM)

        topMiddle = (outerCircleRect.topRight() - outerCircleRect.topLeft()) / 2 + outerCircleRect.topLeft()
        bottomMiddle = (outerCircleRect.bottomRight() - outerCircleRect.bottomLeft()) / 2 + outerCircleRect.bottomLeft()

        shapePainter = QPainter(self)
        shapePainter.setRenderHint(shapePainter.Antialiasing)
        # shapePainter.setPen(QPen(QColor(14,125,145),  OUTERLINEWIDTH, Qt.SolidLine))
        # shapePainter.drawArc(outerCircleRect, CIRCLE/2, CIRCLE/2)

        # shapePainter.setPen(QPen(QColor(14,125,145),  5, Qt.SolidLine))
        # shapePainter.drawLine(topMiddle, bottomMiddle)

        shapePainter.setPen(QPen(QColor(14,125,145),  2, Qt.SolidLine))
        arcRect = QRect(bottomMiddle.x() - 5, bottomMiddle.y()-6, 13, 13)
        shapePainter.drawArc(arcRect, 0, CIRCLE)

        self.pTextEdit.setEnabled(False)
        self.pTextEdit.setVisible(False)

    def drawRectShape(self, event):
        '''
        Draws a rectangle for the textEdit box
        '''
        textBoxRect = self.rect()
        outerCircleRect = self.rect()
        textBoxRect.adjust(+30,+30,-12,-12)
        outerCircleRect.adjust(+8,+8,-8,-15)

        moveRect = QRect(0,0, 11,11)

        shapePainter = QPainter(self)
        shapePainter.setRenderHint(shapePainter.Antialiasing)
        # shapePainter.setPen(QPen(QColor(14,125,145),  5, Qt.SolidLine))
        # shapePainter.drawRect(textBoxRect)

        shapePainter.setPen(QPen(QColor(14,125,145),  5, Qt.SolidLine))
        shapePainter.drawLine(outerCircleRect.topLeft(), outerCircleRect.bottomLeft())

        # shapePainter.setPen(QPen(QColor(14,125,145),  2, Qt.SolidLine))
        # arcRect = QRect(outerCircleRect.bottomLeft().x() - 6, outerCircleRect.bottomLeft().y()+1, 12, 12)
        # shapePainter.drawArc(arcRect, 0, CIRCLE)

        self.pTextEdit.setEnabled(True)
        self.pTextEdit.setVisible(True)

        self.pTextEdit.ensureCursorVisible()
        self.pTextEdit.setFocus()



    def setButtonState(self):
        '''
        Sets the button state depending on the current edit mode
        '''
        if self.editTextBox and self.editMode == editModes.newTextBox:
            self.setEnableOnAllButtonsButThose(['okButton', 'cancelButton'])
            self.setVisibleOnAllButtonsButThose(['okButton', 'cancelButton'])

            self.slider.setVisible(False)

        elif self.editTextBox and self.editMode == editModes.editTextBox:
            self.setEnableOnAllButtonsButThose(['okButton', 'deleteButton'])
            self.setVisibleOnAllButtonsButThose(['okButton', 'deleteButton'])

            self.slider.setVisible(False)

        elif self.editMode == editModes.newTextBox:
            self.setEnableOnAllButtonsButThose(['textButton', 'sizeButton','colorButton'])
            self.setVisibleOnAllButtonsButThose(['textButton', 'sizeButton','colorButton'])

            self.buttons['sizeButton'].move(self.row1Left)
            self.buttons['colorButton'].move(self.row2Left)

        elif self.editMode == editModes.marker:
            self.setEnableOnAllButtonsButThose(['markerButton', 'sizeButton','colorButton'])
            self.setVisibleOnAllButtonsButThose(['markerButton', 'sizeButton','colorButton'])

            self.buttons['sizeButton'].move(self.row1Right)
            self.buttons['colorButton'].move(self.row2Right)

        elif self.editMode == editModes.freehand:
            self.setEnableOnAllButtonsButThose(['freehandButton', 'sizeButton','colorButton'])
            self.setVisibleOnAllButtonsButThose(['freehandButton', 'sizeButton','colorButton'])

            self.buttons['sizeButton'].move(self.row1Right)
            self.buttons['colorButton'].move(self.row2Right)

        elif self.editMode == editModes.eraser:
            self.setEnableOnAllButtonsButThose(['eraserButton'])

        elif self.editMode == editModes.forms:
            self.setEnableOnAllButtonsButThose(['formsButton'])

        elif self.editMode == editModes.markdown:
            self.setEnableOnAllButtonsButThose(['markdownButton'])

        elif self.editMode == editModes.none:
            self.setVisibleOnAllButtonsButThose(['textButton', 'eraserButton', 'formsButton', 'freehandButton', 'markerButton', 'markdownButton', 'undoButton', 'redoButton'])

            self.setEnableOnAllButtonsButThose(['textButton', 'eraserButton', 'formsButton', 'freehandButton', 'markerButton', 'markdownButton', 'undoButton', 'redoButton'])

            self.setCheckedOnAllButtonsButThose([])

            self.slider.setVisible(True)

    def setEnableOnAllButtonsButThose(self, names, value=False):
        for buttonName, buttonInst in self.buttons.items():
            if not buttonName in names:
                buttonInst.setEnabled(value)
            else:
                buttonInst.setEnabled(not value)


    def setVisibleOnAllButtonsButThose(self, names, value=False):
        for buttonName, buttonInst in self.buttons.items():
            if not buttonName in names:
                buttonInst.setVisible(value)
            else:
                buttonInst.setVisible(not value)

    def setCheckedOnAllButtonsButThose(self, names, value=False):
        for buttonName, buttonInst in self.buttons.items():
            if not buttonName in names:
                buttonInst.setChecked(value)
            else:
                buttonInst.setChecked(not value)

    def insertCurrentContent(self, content):
        '''
        Used to append the provided content to the textEdit box

        :param content: Text which should be displayed in the textEdit
        '''
        if content != "":
            self.pTextEdit.setText(content)
            return True
        else:
            self.pTextEdit.setText("")
            return False

    def mousePressEvent(self, event):
        '''
        Overrides the default event
        '''
        self.__mousePressPos = None
        self.__mouseMovePos = None
        if event.button() == Qt.LeftButton:
            self.__mousePressPos = event.globalPos()
            self.__mouseMovePos = event.globalPos()

        QWidget.mousePressEvent(self, event)

    def mouseMoveEvent(self, event):
        '''
        Overrides the default event
        '''
        if event.buttons() == Qt.LeftButton:
            try:
                # adjust offset from clicked point to origin of widget
                currPos = self.mapToGlobal(self.pos())
                globalPos = event.globalPos()
                diff = globalPos - self.__mouseMovePos
                newPos = self.mapFromGlobal(currPos + diff)
                self.move(newPos)

                self.__mouseMovePos = globalPos
            except AttributeError:
                pass    # We are in touch screen mode here

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
        self.currentContent = currentContent

        if self.insertCurrentContent(currentContent):
            self.editMode = editModes.editTextBox
        else:
            self.editMode = editModes.newTextBox

        self.editTextBox = True
        self.setButtonState()

        self.currentX = x
        self.currentY = y
        self.repaint()

    def handleTextButton(self):
        if self.textButton.isChecked():
            self.editMode = editModes.newTextBox
        else:
            self.editMode = editModes.none

        self.editModeChange.emit(self.editMode)
        self.setButtonState()

    def handleMarkerButton(self):
        if self.markerButton.isChecked():
            self.editMode = editModes.marker
        else:
            self.editMode = editModes.none

        self.editModeChange.emit(self.editMode)
        self.setButtonState()

    def handleEraserButton(self):
        if self.eraserButton.isChecked():
            self.editMode = editModes.eraser
        else:
            self.editMode = editModes.none

        self.editModeChange.emit(self.editMode)
        self.setButtonState()

    def handleFormsButton(self):
        if self.formsButton.isChecked():
            self.editMode = editModes.forms
        else:
            self.editMode = editModes.none

        self.editModeChange.emit(self.editMode)
        self.setButtonState()

    def handleFreehandButton(self):
        if self.freehandButton.isChecked():
            self.editMode = editModes.freehand
        else:
            self.editMode = editModes.none

        self.editModeChange.emit(self.editMode)
        self.setButtonState()

    def handleMarkdownButton(self):
        if self.markdownButton.isChecked():
            self.editMode = editModes.markdown
        else:
            self.editMode = editModes.none

        self.editModeChange.emit(self.editMode)
        self.setButtonState()

    def handleOkButton(self):
        '''
        This method handles all the stuff that needs to be done, when the user successfully finished textEditing
        '''
        if self.editMode == editModes.newTextBox or self.editMode == editModes.editTextBox:
            self.textInputFinished.emit(self.currentX, self.currentY, self.currentPageNumber, True, self.pTextEdit.toPlainText())
            self.editMode = editModes.none
            self.editTextBox = False
            self.setButtonState()

            self.repaint()
            self.currentPageNumber = -1
            self.currentX = -1
            self.currentY = -1

    def handleCancelButton(self):
        '''
        This method handles all the stuff that needs to be done, when the user canceled textEditing
        '''
        if self.editMode == editModes.newTextBox or self.editMode == editModes.editTextBox:
            self.textInputFinished.emit(self.currentX, self.currentY, self.currentPageNumber, False, self.currentContent)
            self.editMode = editModes.none
            self.editTextBox = False
            self.setButtonState()

            self.repaint()
            self.currentPageNumber = -1
            self.currentX = -1
            self.currentY = -1


    def handleDeleteButton(self):
        '''
        This method handles all the stuff that needs to be done, when the user canceled textEditing
        '''
        if self.editMode == editModes.newTextBox or self.editMode == editModes.editTextBox:
            self.textInputFinished.emit(self.currentX, self.currentY, self.currentPageNumber, False, "")
            self.editMode = editModes.none
            self.editTextBox = False
            self.setButtonState()

            self.repaint()
            self.currentPageNumber = -1
            self.currentX = -1
            self.currentY = -1

    def handleUndoButton(self):
        History.undo()
        self.suggestUpdate.emit()

    def handleRedoButton(self):
        pass

    def restoreSliderValue(self):
        try:
            if self.sizeButton.isChecked():
                if self.editMode == editModes.newTextBox:
                    lastSliderValue = int(Preferences.data['textSize'])
                elif self.editMode == editModes.marker:
                    lastSliderValue = int(Preferences.data['markerSize'])
                elif self.editMode == editModes.freehand:
                    lastSliderValue = int(Preferences.data['freehandSize'])

            elif self.colorButton.isChecked():
                if self.editMode == editModes.marker:

                    normRGB = tuple(map(lambda x: float(x), str(Preferences.data['markerColor'])))
                    hsv = colorsys.rgb_to_hsv(*normRGB)

                    lastSliderValue = int(hsv[0] * 100)
                elif self.editMode == editModes.freehand:
                    normRGB = tuple(map(lambda x: float(x), str(Preferences.data['freehandColor'])))
                    hsv = colorsys.rgb_to_hsv(*normRGB)

                    lastSliderValue = int(hsv[0] * 100)

        except ValueError:
            self.storeSliderValue()
            return



        self.slider.setValue(lastSliderValue)


    def storeSliderValue(self):
        if self.sizeButton.isChecked():
            if self.editMode == editModes.newTextBox:
                Preferences.updateKeyValue('textSize', self.slider.value())
            elif self.editMode == editModes.marker:
                Preferences.updateKeyValue('markerSize', self.slider.value())
            elif self.editMode == editModes.freehand:
                Preferences.updateKeyValue('freehandSize', self.slider.value())
        elif self.colorButton.isChecked():
            normRGB = colorsys.hsv_to_rgb(self.slider.value() / 100,1,1)

            if self.editMode == editModes.marker:
                Preferences.updateKeyValue('markerColor', tuple(map(lambda x: str(x), normRGB)))
            elif self.editMode == editModes.freehand:
                Preferences.updateKeyValue('freehandColor', tuple(map(lambda x: str(x), normRGB)))

    def handleSizeButton(self):
        '''
        This method will set the slider value to match the current size
        '''
        if self.sizeButton.isChecked():
            self.slider.setEnabled(True)
            self.restoreSliderValue()
        else:
            self.storeSliderValue()

            self.slider.setEnabled(False)
            self.slider.setValue(100)

    def handleColorButton(self):
        '''
        Handles color button presses
        '''
        if self.colorButton.isChecked():
            self.slider.setEnabled(True)
            self.restoreSliderValue()
        else:
            self.restoreDefaults()

            self.slider.setEnabled(False)
            self.slider.setValue(100)

    def handleSliderValueChange(self, value):
        '''
        Triggered when user changes the slider value
        '''
        pass

    def handleSliderValueChanged(self):
        '''
        Triggered when user has changed the slider value
        '''
        self.storeSliderValue()
