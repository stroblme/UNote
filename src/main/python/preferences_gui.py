# ---------------------------------------------------------------
# -- Preferences GUI Main File --
#
# Main File for running the Preferences GUI
#
# Author: Melvin Strobl
# ---------------------------------------------------------------

from fbs_runtime.application_context.PyQt5 import ApplicationContext

import os  # launching external python script
import sys  # exit script, file parsing

from PyQt5.QtWidgets import QGraphicsDropShadowEffect
from PyQt5.QtGui import QColor

from PyQt5.QtCore import pyqtSignal, QSettings, QObject, Qt
from PyQt5.QtWidgets import QDialog
from PyQt5.QtGui import QIcon

from util import readFile, writeFile, toBool

from preferences_receiver import Receivers
from preferences import Preferences
from guiHelper import GuiHelper

# Reload the main ui

from preferences_qt_export import Ui_PreferencesDialog




class App(Ui_PreferencesDialog):
    appctxt = ApplicationContext()

    ICONPATH = appctxt.get_resource('icon.png')

    COMPANY_NAME = "MSLS"
    APPLICATION_NAME = "UNote"

    KEYSFILEPATH = "./preferences.keys"

class PreferencesGUI(App):
    '''
    Main class for the Preferences Window
    '''
    keys = list()

    def __init__(self):
        super().__init__()
        self.initUI()

        # self.MainWindow.setWindowFlags(QtCore.Qt.WindowTitleHint | QtCore.Qt.FramelessWindowHint)

        # self.MainWindow.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        self.settings = QSettings(self.COMPANY_NAME, self.APPLICATION_NAME)

        self.rec = Receivers()
        self.connectReceivers(self.rec)

        self.guiHelper = GuiHelper()

        self.loadKeys()

        self.loadSettings()

        self.applySettings()

    def __exit__(self, exc_type, exc_value, traceback):
        del self.settings


    def initUI(self):
        # self.app = QtWidgets.QApplication(sys.argv)
        self.MainWindow = QDialog()
        self.ui = Ui_PreferencesDialog()
        self.ui.setupUi(self.MainWindow)

        self.MainWindow.setAttribute(Qt.WA_TranslucentBackground)
        self.backgroundEffect = QGraphicsDropShadowEffect(self.MainWindow)
        self.backgroundEffect.setBlurRadius(30)
        self.backgroundEffect.setOffset(0,0)
        self.backgroundEffect.setEnabled(True)


        self.ui.centralwidget.setGraphicsEffect(self.backgroundEffect)

        self.MainWindow.setWindowIcon(QIcon(self.ICONPATH))
        self.MainWindow.setWindowFlags(Qt.WindowTitleHint | Qt.FramelessWindowHint)


    def run(self):
        '''
        Starts the Preferences Window
        '''
        self.loadSettings()
        self.MainWindow.show()

        result = self.MainWindow.exec_()

        #settings confirmed
        if result:
            self.saveSettings()
        else:
            self.discardSettings()

    def connectReceivers(self, receiversInst):
        '''
        Connects all the buttons to the right receivers
        '''
        self.ui.radioButtonDarkTheme.toggled.connect(lambda: receiversInst.setTheme(self.ui))

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

        print("Settings saved")


    def storeLooseEntries(self):
        '''
        Saves all entries, which have been entered without explicit confirmation
        '''
        Preferences.updateKeyValue("radioButtonDarkTheme", str(self.ui.radioButtonDarkTheme.isChecked()))
        Preferences.updateKeyValue("radioButtonPenOnly", str(self.ui.radioButtonPenOnly.isChecked()))
        Preferences.updateKeyValue("comboBoxAutosave", str(self.ui.comboBoxAutosave.currentText()))


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
        self.ui.comboBoxAutosave.setCurrentText(str(Preferences.data["comboBoxAutosave"]))

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
