import sys, os

def saveNewPDF(fileName):
    pass

def overwritePDF(fileName):
    pass

def generatePdfName(filePath):
    name, ext = os.path.splitext(self.filename)
    name = name + '_m'

    newFileName = name + ext

    if os.path.isfile(newFileName):
        return
