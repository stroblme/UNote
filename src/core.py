# ---------------------------------------------------------------
# -- CXP Test GUI Core File --
#
# Implements core functionality
#
# Author: Melvin Strobl
# ---------------------------------------------------------------

from interfaces import IregCon, IcsrCtrl
from preferences import Preferences

import subprocess  # for running external cmds
import os

class RegisterMapHandler(IregCon):
    '''
    Class for handling the register map
    '''
    registerMapLoaded = False
    pickleDictLoaded = False

    def convertRegisterMap(self, inputPath, outputPath="./cache/regCon"):
        '''
        Loads a register map from a given filepath
        '''

        if self.IconvertRegisterMap(inputPath, outputPath):
            self.registerMapLoaded = True
            return True

        return False

    def loadRegisterMap(self, pickleDictFilePath):
        '''
        Loads a register map from a given filepath
        '''

        if self.IloadRegisterMap(pickleDictFilePath):
            self.pickleDictFilePath = pickleDictFilePath

            self.pickleDictLoaded = True

            return True
        return False

    def getRegisterAddress(self, registerName, pickleDictFilePath = None):
        if not self.pickleDictLoaded:
            self.loadRegisterMap(pickleDictFilePath)

        return self.IgetRegisterAddress(registerName)

    

class ConnectionHandler(IcsrCtrl):
    connectionIsOpen = False
    debugMode = False
    
    def listAvailablePorts(self):
        '''
        List the available port
        '''
        return self.IlistConnections()

    def openConnection(self, port, baud):
        if port is None or baud is None:
            raise Exception("You must specify a port and baud")

        if port == "debug" and baud == "debug":
            self.connectionIsOpen = True
            
            self.port = port
            self.baud = baud

            self.debugMode = True
            print("Connection opened in debug mode")

        elif self.IopenConnection(port, baud):
            self.connectionIsOpen = True

            self.port = port
            self.baud = baud

            print("Connection opened")
            
    def closeConnection(self):
        if self.connectionIsOpen and not self.debugMode:
            self.IcloseConnection()

            print("Connection closed")
        else:
            print("Connection not open")
            
    def verifyConnection(self, port = None, baud = None):
        if not self.connectionIsOpen:
            self.openConnection(port, baud)

        if self.debugMode:
            return True

        try:
            self.IverifyConnection(port, baud)
            return True
        except:
            return False

    def writeRegister(self, address, data, port = None, baud = None):
        if not self.connectionIsOpen:
            self.openConnection(port, baud)

        if self.debugMode:
            return "Success"

        return self.IwriteRegister(address, data)

    def readRegister(self, address, port = None, baud = None):
        if not self.connectionIsOpen:
            self.openConnection(port, baud)
            
        if self.debugMode:
            return 123456789

        return self.IreadRegister(address)


