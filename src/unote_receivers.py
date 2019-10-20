# ---------------------------------------------------------------
# -- CXP Test GUI Receivers File --
#
# Receivers for handling events on the cxptest gui
#
# Author: Melvin Strobl
# ---------------------------------------------------------------

from PySide2 import QtCore
from PySide2.QtCore import Signal, Qt, QObject, Slot

import json

from preferences import Preferences

from guiHelper import GuiHelper
from logHelper import LogHelper

class Receivers(QObject):
    '''
    Class for handling all the event calls from the ui
    '''

    SigSendMessageToJS = Signal(str)

    def __init__(self, uiInst):
        super().__init__()

        self.uiInst = uiInst

        self.guiHelper = GuiHelper()


    def openPreferencesReceiver(self, preferenceInstance):
        '''
        Opens the Preference Window
        '''
        preferenceInstance.run()


    def setLogHelperInst(self, logHelper):
        '''
        Used to set the log helper instance after instantiating the cxptest_receiver obj
        '''
        self.logHelper = logHelper

    @Slot(str)
    def JSSendMessage(self, msg):
        '''
        This method is called each time the webviewer receives a user input.
        msg is a valid json object, containing the following data
        name, id, value
        '''



    def JSReceiveMessage(self, msg):
        '''
        This method provides the interface for sending content in json format to the html viewer.
        A valid json msg contains:
        name, id, value
        '''
        self.SigSendMessageToJS.emit(msg)