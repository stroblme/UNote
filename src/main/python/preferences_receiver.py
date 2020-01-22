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

    @Slot(int)
    def setTheme(self, index):
        '''
        Apply the selected theme
        '''

        if self.ui.comboBoxThemeSelect.currentIndex() == 0:
            self.guiHelper.toggle_stylesheet(":/dark.qss")
        elif self.ui.comboBoxThemeSelect.currentIndex() == 1:
            self.guiHelper.toggle_stylesheet(":/light.qss")

        Preferences.updateKeyValue("comboBoxThemeSelect", self.ui.comboBoxThemeSelect.currentIndex())

    def setAutoSave(self):
        if self.ui.comboBoxAutosave.currentIndex() != 0:
            interval = 1000 * 5 * self.ui.comboBoxAutosave.currentIndex()   # ui displays 5 minute intervals

            Preferences.updateKeyValue('autosaveSetting', interval)

            self.autoSaveTimer.timeout.connect(self.ui.graphicsView.savePdf)
            self.autoSaveTimer.start(interval)
        else:
            self.autoSaveTimer.stop()
