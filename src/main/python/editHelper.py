from PyQt5.QtCore import pyqtSignal, pyqtSlot, QObject

class editModes(QObject):
    '''
    This class contains all available edit modes for the current pdf
    '''
    none = 'none'
    mark = 'mark'
    newTextBox = 'newTextBox'
    editTextBox = 'editTextBox'

    _editModes__current = none

    @staticmethod
    def setMode(mode):
        __current = mode

    @staticmethod
    def getMode():
        return __current

    @staticmethod
    def notify():
        editModeUpdate.emit()
