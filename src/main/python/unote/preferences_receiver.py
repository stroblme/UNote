# ---------------------------------------------------------------
# -- Preferences Receivers File --
#
# Receivers for handling events on the Preferences
#
# Author: Melvin Strobl
# ---------------------------------------------------------------
from PyQt5.QtCore import QObject

from guiHelper import GuiHelper
from preferences import Preferences

class Receivers(QObject):
    '''
    Class for handling all the event calls from the ui
    '''

    def __init__(self):
        super().__init__()

        self.guiHelper = GuiHelper()

    def setTheme(self, uiInst):
        '''
        Apply the selected theme
        '''

        if uiInst.radioButtonDarkTheme.isChecked():
            self.guiHelper.toggle_stylesheet(":/dark.qss")
        else:
            self.guiHelper.toggle_stylesheet(":/light.qss")

        Preferences.updateKeyValue("radioButtonDarkTheme", uiInst.radioButtonDarkTheme.isChecked())
