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
        Preferences.updateKeyValue("radioButtonAffectsPDF", str(self.ui.radioButtonAffectsPDF.isChecked()))
        
    @Slot(int)
    def setComboBoxThemeSelect(self, index):
        '''
        Apply the selected theme
        '''

        if self.ui.comboBoxThemeSelect.currentIndex() == 0:
            self.guiHelper.toggle_stylesheet(":/dark.qss")
        else:
            self.guiHelper.toggle_stylesheet(":/light.qss")

        Preferences.updateKeyValue("comboBoxThemeSelect", self.ui.comboBoxThemeSelect.currentIndex())


    def setRadioButtonPenDrawOnly(self):
        Preferences.updateKeyValue("radioButtonPenDrawOnly", str(self.ui.radioButtonPenDrawOnly.isChecked()))

    @Slot(int)
    def setComboBoxDrawingMode(self, index):
        Preferences.updateKeyValue("comboBoxDrawingMode", self.ui.comboBoxDrawingMode.currentIndex())


    def setRadioButtonSaveOnExit(self):
        Preferences.updateKeyValue("radioButtonSaveOnExit", str(self.ui.radioButtonSaveOnExit.isChecked()))

    @Slot(int)
    def setComboBoxAutosaveMode(self, index):
        Preferences.updateKeyValue("comboBoxAutosaveMode", self.ui.comboBoxAutosaveMode.currentIndex())
