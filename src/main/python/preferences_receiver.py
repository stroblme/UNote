# ---------------------------------------------------------------
# -- Preferences Receivers File --
#
# Receivers for handling events on the Preferences
#
# Author: Melvin Strobl
# ---------------------------------------------------------------
from PySide2.QtCore import QObject, Signal

from guiHelper import GuiHelper
from preferences import Preferences

class Receivers(QObject):
    '''
    Class for handling all the event calls from the ui
    '''
    confirmSignal = Signal(bool)

    def __init__(self, uiInst):
        super().__init__()

        self.guiHelper = GuiHelper()

        self.uiInst = uiInst

    def confirmReceiver(self):

        self.uiInst.windowInst.hide()
        self.confirmSignal.emit(True)

    def rejectReceiver(self):

        self.uiInst.windowInst.hide()
        self.confirmSignal.emit(False)

    def setTheme(self):
        '''
        Apply the selected theme
        '''

        if self.uiInst.radioButtonDarkTheme.isChecked():
            self.guiHelper.toggle_stylesheet(":/dark.qss")
        else:
            self.guiHelper.toggle_stylesheet(":/light.qss")

        Preferences.updateKeyValue("radioButtonDarkTheme", self.uiInst.radioButtonDarkTheme.isChecked())
