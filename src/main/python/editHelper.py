from PySide2.QtCore import Signal, Slot, QObject

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
