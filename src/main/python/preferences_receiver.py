# ---------------------------------------------------------------
# -- Preferences Receivers File --
#
# Receivers for handling events on the Preferences
#
# Author: Melvin Strobl
# ---------------------------------------------------------------
from PySide2.QtCore import QObject, Signal, Slot, QTimer

from guiHelper import GuiHelper
from preferences import Preferences

class Receivers(QObject):
    '''
    Class for handling all the event calls from the ui
    '''
    confirmSignal = Signal(bool)

    def __init__(self, ui):
        super().__init__()

        self.guiHelper = GuiHelper()

        self.ui = ui

        self.autoSaveTimer = QTimer()

    def confirmReceiver(self):

        self.ui.windowInst.hide()
        self.confirmSignal.emit(True)

    def rejectReceiver(self):

        self.ui.windowInst.hide()
        self.confirmSignal.emit(False)

    def setRadioButtonAffectsPDF(self):
        Preferences.updateKeyValue("radioButtonAffectsPDF", str(self.uiInst.radioButtonAffectsPDF.isChecked()))
        
    @Slot(int)
    def setComboBoxThemeSelect(self, index):
        '''
        Apply the selected theme
        '''

        if self.uiInst.comboBoxThemeSelect.currentIndex() == 0:
            self.guiHelper.toggle_stylesheet(":/dark.qss")
        elif self.uiInst.comboBoxThemeSelect.currentIndex() == 1:
            self.guiHelper.toggle_stylesheet(":/light.qss")

        Preferences.updateKeyValue("comboBoxThemeSelect", self.uiInst.comboBoxThemeSelect.currentIndex())


    def setRadioButtonPenDrawOnly(self):
        Preferences.updateKeyValue("radioButtonPenDrawOnly", str(self.uiInst.radioButtonPenDrawOnly.isChecked()))

    @Slot(int)
    def setComboBoxDrawingMode(self, index):
        Preferences.updateKeyValue("comboBoxDrawingMode", self.uiInst.comboBoxDrawingMode.currentIndex())


    def setRadioButtonSaveOnExit(self):
        Preferences.updateKeyValue("radioButtonSaveOnExit", str(self.uiInst.radioButtonSaveOnExit.isChecked()))

    @Slot(int)
    def setComboBoxAutosaveMode(self, index):
        Preferences.updateKeyValue("comboBoxAutosaveMode", self.uiInst.comboBoxAutosaveMode.currentIndex())
