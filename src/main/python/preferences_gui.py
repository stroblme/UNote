# ---------------------------------------------------------------
# -- Preferences GUI Main File --
#
# Main File for running the Preferences GUI
#
# Author: Melvin Strobl
# ---------------------------------------------------------------

from fbs_runtime.application_context.PySide2 import ApplicationContext

import os  # launching external python script
import sys  # exit script, file parsing

from PySide2.QtWidgets import QGraphicsDropShadowEffect
from PySide2.QtGui import QColor

from PySide2.QtCore import Signal, Slot, QSettings, QObject, Qt
from PySide2.QtWidgets import QDialog
from PySide2.QtGui import QIcon

from util import readFile, writeFile, toBool

from preferences_receiver import Receivers
from preferences import Preferences
from guiHelper import GuiHelper

# Reload the main ui

from preferences_qt_export import Ui_PreferencesDialog




class App(QObject):
    COMPANY_NAME = "MSLS"
    APPLICATION_NAME = "UNote"

    KEYSFILEPATH = "./preferences.keys"

class PreferencesGUI(App):
    '''
    Main class for the Preferences Window
    '''
    keys = list()
    finished = Signal()


    def __init__(self, appctxt, windowInst):
        super().__init__()
        self.appctxt = appctxt
        self.initUI(windowInst)

        # self.windowInst.setWindowFlags(QtCore.Qt.WindowTitleHint | QtCore.Qt.FramelessWindowHint)

        # self.windowInst.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        self.settings = QSettings(self.COMPANY_NAME, self.APPLICATION_NAME)

        self.receiversInst = Receivers(self.ui)
        self.receiversInst.confirmSignal.connect(self.handleExit)
        self.connectReceivers()

        self.guiHelper = GuiHelper()

        self.loadKeys()

        self.loadSettings()

        self.applySettings()

    def __exit__(self, exc_type, exc_value, traceback):
        del self.settings


    def initUI(self, windowInst):
        # self.app = QtWidgets.QApplication(sys.argv)
        self.ui = Ui_PreferencesDialog()
        self.ui.windowInst = windowInst
        self.ui.windowInst.hide()
        self.ui.setupUi(self.ui.windowInst)

        windowInst.setAttribute(Qt.WA_TranslucentBackground)
        self.backgroundEffect = QGraphicsDropShadowEffect(windowInst)
        self.backgroundEffect.setBlurRadius(30)
        self.backgroundEffect.setOffset(0,0)
        self.backgroundEffect.setEnabled(True)


        self.ui.centralwidget.setGraphicsEffect(self.backgroundEffect)


    def run(self):
        '''
        Starts the Preferences Window
        '''
        self.loadSettings()
        self.ui.windowInst.show()

    @Slot(bool)
    def handleExit(self, confirmed):
        if confirmed:
            self.storeLooseEntries()
            self.storeSettings()

            print('Settings saved')
        else:
            self.loadSettings()

            print('Settings discarded')

        self.finished.emit()

    def connectReceivers(self):
        '''
        Connects all the buttons to the right receivers
        '''
        self.ui.radioButtonDarkTheme.toggled.connect(lambda: self.receiversInst.setTheme())
        self.ui.pushButtonOk.clicked.connect(lambda:self.receiversInst.confirmReceiver())
        self.ui.pushButtonCancel.clicked.connect(lambda:self.receiversInst.rejectReceiver())

    def loadKeys(self):
        '''
        Load the preferences keys
        '''

        scriptPath = os.path.dirname(os.path.abspath(__file__)) + '\\'
        # absKeysFilePath = os.path.normpath(scriptPath + KEYSFILEPATH)
        absKeysFilePath = self.appctxt.get_resource('preferences.keys')

        keysFileContent = readFile(absKeysFilePath)

        for key in keysFileContent['lines']:
            self.keys.append(key.replace('\n',''))

    def storeSettings(self):
        '''
        Store the settings from the gui to the local dict and then to the settings instance
        '''
        for key in self.keys:
            self.settings.setValue(key, str(Preferences.data[key]))

        self.settings.sync()

    def storeLooseEntries(self):
        '''
        Saves all entries, which have been entered without explicit confirmation
        '''
        Preferences.updateKeyValue("radioButtonDarkTheme", str(self.ui.radioButtonDarkTheme.isChecked()))
        Preferences.updateKeyValue("radioButtonPenOnly", str(self.ui.radioButtonPenOnly.isChecked()))
        Preferences.updateKeyValue("spinBoxAutosave", int(self.ui.spinBoxAutosave.currentText()))


    def saveSettings(self):
        self.storeLooseEntries()
        self.storeSettings()

    def discardSettings(self):
        self.loadSettings()

    def loadSettings(self):
        '''
        Load the settings from the settings instance to the local dict
        '''
        for key in self.keys:
            Preferences.updateKeyValue(key, self.settings.value(key, defaultValue=None, type=str))

        self.ui.radioButtonDarkTheme.setChecked(toBool(Preferences.data["radioButtonDarkTheme"]))
        self.ui.radioButtonPenOnly.setChecked(toBool(Preferences.data["radioButtonPenOnly"]))
        try:
            self.ui.spinBoxAutosave.setValue(int(Preferences.data["spinBoxAutosave"]))
        except ValueError as identifier:
            self.ui.spinBoxAutosave.setValue(10)


    def applySettings(self):
        '''
        Apply the settings from the local dict to the gui instance
        '''
        if toBool(Preferences.data["radioButtonDarkTheme"]) == True:
            self.guiHelper.toggle_stylesheet(":/dark.qss")
            self.backgroundEffect.setColor(QColor(100,100,100))

        else:
            self.guiHelper.toggle_stylesheet(":/light.qss")
            self.backgroundEffect.setColor(QColor(0,0,0))
