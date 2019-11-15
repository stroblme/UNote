# ---------------------------------------------------------------
# -- Preferences GUI Main File --
#
# Main File for running the Preferences GUI
#
# Author: Melvin Strobl
# ---------------------------------------------------------------

from fbs_runtime.application_context.PyQt5 import ApplicationContext

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import pyqtSignal, QSettings, QObject
from PyQt5.QtWidgets import QDialog


from util import readFile, writeFile

from preferences_receiver import Receivers
from preferences import Preferences
from guiHelper import GuiHelper


import os  # launching external python script
import sys  # exit script, file parsing
import subprocess  # for running external cmds

# Reload the main ui

sys.path.append('./ui')
from ui import Ui_PreferencesDialog

COMPANY_NAME = "MSLS"
APPLICATION_NAME = "UNote"

KEYSFILEPATH = "./preferences.keys"


class App(Ui_PreferencesDialog):
    appctxt = ApplicationContext()

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

        self.settings = QSettings(COMPANY_NAME, APPLICATION_NAME)

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

        self.MainWindow.setWindowIcon(QtGui.QIcon(":/assets/icon.png"))

    def run(self):
        '''
        Starts the Preferences Window
        '''
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
        self.ui.radioButtonDarkTheme.toggled.connect(lambda:receiversInst.setTheme(self.ui))

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

        self.ui.radioButtonDarkTheme.setChecked(bool(Preferences.data["radioButtonDarkTheme"]))

    def applySettings(self):
        '''
        Apply the settings from the local dict to the gui instance
        '''
        if bool(Preferences.data["radioButtonDarkTheme"]) == True:
            self.guiHelper.toggle_stylesheet(":/dark.qss")
        else:
            self.guiHelper.toggle_stylesheet(":/light.qss")
