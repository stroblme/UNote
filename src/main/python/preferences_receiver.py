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

    def setRegisterMapFile(self, uiInst):
        '''
        Runs file dialog window and stores the selected path
        '''

        path = self.guiHelper.openFileNameDialog("*.xlsx")

        if not path:
            return

        uiInst.lineEditRegisterMapFile.setText(path)

        Preferences.updateKeyValue("lineEditRegisterMapFile", path)

    def setRegConExecutablePath(self, uiInst):
        '''
        Runs file dialog window and stores the selected path
        '''

        path = self.guiHelper.openFileNameDialog("*.exe")

        if not path:
            return

        uiInst.lineEditRegConExecutablePath.setText(path)

        Preferences.updateKeyValue("lineEditRegConExecutablePath", path)

    def setConvertRegisterMapOnStartup(self, uiInst):
        '''
        Stores the selected option
        '''

        Preferences.updateKeyValue("radioButtonConvertRegisterMapOnStartup", uiInst.radioButtonConvertRegisterMapOnStartup.isChecked())

    def setRegisterAccessExecutablePath(self, uiInst):
        '''
        Runs file dialog window and stores the selected path
        '''

        path = self.guiHelper.openFileNameDialog("*.py")

        if not path:
            return

        uiInst.lineEditRegisterAccessPath.setText(path)

        Preferences.updateKeyValue("lineEditRegisterAccessPath", path)

    def setBoardCtrlExecutablePath(self, uiInst):
        '''
        Runs file dialog window and stores the selected path
        '''

        path = self.guiHelper.openFileNameDialog("*.py")

        if not path:
            return

        uiInst.lineEditBoardControlPath.setText(path)

        Preferences.updateKeyValue("lineEditBoardControlPath", path)
