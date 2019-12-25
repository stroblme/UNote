import sys
from indexed import IndexedOrderedDict

class History():

    timeline = IndexedOrderedDict()
    pointer = 0 # Latest pointer

    def __init__(self):
        pass

    @staticmethod
    def undo():
        # Go back in time
        History.pointer -= 1

        action = History.timeline[History.pointer]

        action["undoFuncHandle"](action["undoFuncParam"])

    @staticmethod
    def redo():
        # Go back in time
        History.pointer += 1

        action = History.timeline[History.pointer]

        action["undoFuncHandle"](action["undoFuncParam"])

    @staticmethod
    def addToHistory(undoFuncHandle, undoFuncParam):
        action = {"undoFuncHandle":undoFuncHandle, "undoFuncParam":undoFuncParam}

        # Add action to timeline
        History.timeline[History.pointer] = action
        # Increment timeline
        History.pointer += 1

    @staticmethod
    def removeFromHistory():
        pass
