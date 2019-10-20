# ---------------------------------------------------------------
# -- CXP Test GUI Interfaces File --
#
# Interfaces between external scripts and the CXP Test GUI
#
# Author: Melvin Strobl
# ---------------------------------------------------------------

import sys
import os
import pickle
import subprocess



class IcsrCtrl():

    def __init__(self, csrCtrlPath):
        self.csrCtrlPath = csrCtrlPath
        sys.path.append(os.path.dirname(self.csrCtrlPath))

        try:
            from csrCtrl import CsrCtrl as CsrCtrl
        except ImportError as e:
            print("Unable to import csrCtrl class. Please verify the filepath: " + self.csrCtrlPath)
            self.classValid = False
            return

        print("successfully imported csrCtrl class")
        self.classValid = True

    def IlistConnections(self):
        '''
        Retrieves the available ports directly from the serial library
        '''
        comlist = serial.tools.list_ports.comports()
        connected = []
        for element in comlist:
            connected.append(element.device)

        return connected

    def IverifyConnection(self, port, baud):
        '''
        Verifies the selected com port by trying to read the device id
        '''


        try:
            print(self.csrCtrl.csr_read(0x00))
        except Exception as identifier:
            print("Unable to readback from address 0x00 " + str(identifier))

    def IopenConnection(self, port, baud):
        if not self.classValid:
            raise Exception("Cannot verify connection without a valid csrClass")
        else:
            from csrCtrl import CsrCtrl as CsrCtrl


        try:
            self.csrCtrl = CsrCtrl(port, baud)

            print("Successfully opened port " + port + " with baud " + baud)
            return True
        except Exception as identifier:
            print("Unable to open port: " + str(identifier))
            return False


    def IcloseConnection(self):
        try:
            self.csrCtrl.close()
            return True
        except Exception as identifier:
            print("Unable to close connection: " + str(identifier))
            return False

    def IwriteRegister(self, address, data):
        if not self.csrCtrl:
            print("Would now write " + str(data) + " at address " + str(address))

        try:
            resp = self.csrCtrl.csr_write(address, data)
        except Exception as identifier:
            print("Unable to write data " + str(data) + " at address " + str(address) + "\n" + str(identifier))
            return False

        return True

    def IreadRegister(self, address):
        if not self.csrCtrl:
            print("Would now read from address " + str(address))
            return 123456789

        try:
            resp = self.csrCtrl.csr_read(address)
            return resp
        except Exception as identifier:
            print("Unable to read from address " + str(address) + "\n" + str(identifier))
            return None

class IregCon():

    ADDRESS_INDEX = 0
    REGISTERNAME_INDEX = 1
    FIELDNAME_INDEX = 2
    SIZE_INDEX = 3
    HIGH_INDEX = 4
    LOW_INDEX = 5
    ACCESS_INDEX = 6
    DEFAULT_INDEX = 7
    SIGNAL_INDEX = 8
    CLOCKDOMAIN_INDEX = 9
    SCANMODE_INDEX = 10
    DESCRIPTION_INDEX = 11
    ENUM_INDEX = 12

    def __init__(self, regConPath):
        self.regConPath = regConPath

    def IconvertRegisterMap(self, inputFile, regConOutFolder):
        cmd = self.regConPath + " -i " + inputFile + " -o " + regConOutFolder + " -q"

        FNULL = open(os.devnull, 'w')

        print("Running RegCon")

        try:
            subprocess.call(cmd, stdout=FNULL, stderr=subprocess.STDOUT)

            return True
        except Exception as identifier:
            print("Unable to run regCon " + str(identifier))

    def IloadRegisterMap(self, pickleDictFilePath):
        try:

            with open(pickleDictFilePath, 'rb') as f:
                self.registerMap = pickle.load(f)

            self.colList = self.registerMap['colList']
            del self.registerMap['colList']
            return True
        except Exception as identifier:
            print("Unable to load register map " + str(identifier))
            return False

    def IgetRegisterAddress(self, registerName):
        registerField = self.registerMap[registerName]

        return registerField.values()[0][self.colList[self.ADDRESS_INDEX]]