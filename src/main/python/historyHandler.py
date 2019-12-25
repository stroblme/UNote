import sys
from indexed import IndexedOrderedDict

class History():

    MAXTIMELINELENGTH = 20
    timeline = list()
    pointer = -1 # Latest pointer

    def __init__(self):
        pass

    @staticmethod
    def undo():
        if History.pointer+1 == len(History.timeline):
            return

        # Go back in time
        History.pointer += 1

        action = History.timeline[History.pointer]

        action["undoFuncHandle"](action["undoFuncParam"])

    @staticmethod
    def redo():
        if History.pointer == -1:
            return

        action = History.timeline[History.pointer]

        # Go back in time
        History.pointer -= 1

        action["undoFuncParam"] = action["redoFuncHandle"](action["redoFuncParam"])

    @staticmethod
    def addToHistory(undoFuncHandle, undoFuncParam, redoFuncHandle, redoFuncParam):
        if History.pointer != -1:
            del History.timeline[0:History.pointer]
            History.pointer = -1

        # Add action to timeline
        History.timeline.insert(0, {"undoFuncHandle":undoFuncHandle, "undoFuncParam":undoFuncParam, "redoFuncHandle":redoFuncHandle, "redoFuncParam":redoFuncParam})

        if len(History.timeline) > History.MAXTIMELINELENGTH:
            del History.timeline[-1]

    @staticmethod
    def removeFromHistory():
        pass
