from PyQt5.QtCore import pyqtSignal, pyqtSlot, QObject

class editModes(QObject):
    '''
    This class contains all available edit modes for the current pdf
    '''
    none = 'none'
    marker = 'marker'
    newTextBox = 'newTextBox'
    editTextBox = 'editTextBox'
    freehand = 'freehand'
    forms = 'forms'
    eraser = 'eraser'
    markdown = 'markdown'
