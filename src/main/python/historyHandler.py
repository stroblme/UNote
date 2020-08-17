import sys
from indexed import IndexedOrderedDict


class History():

    MAXTIMELINELENGTH = 60
    timeline = list()
    pointer = -1 # Latest pointer
    recentChanges = 0

    def __init__(self, parent):
        super().__init__(parent)


    @staticmethod
    def resetHistoryChanges():
        '''
        Called e.g. when the pdf is saved
        '''
        History.recentChanges = 0

    @staticmethod
    def undo():
        if History.pointer+1 == len(History.timeline):
            return

        # Go back in time
        History.pointer += 1

        action = History.timeline[History.pointer]

        if type(action["undoFuncHandle"]) == list:
            action["undoFuncHandle"](*action["undoFuncParam"])
        else:
            action["undoFuncHandle"](action["undoFuncParam"])

        History.recentChanges -= 1

    @staticmethod
    def redo():
        if History.pointer == -1:
            return

        action = History.timeline[History.pointer]

        # Go back in time
        History.pointer -= 1

        if type(action["redoFuncParam"]) == list:
            action["undoFuncParam"] = action["redoFuncHandle"](*action["redoFuncParam"])
        else:
            action["undoFuncParam"] = action["redoFuncHandle"](action["redoFuncParam"])

        History.recentChanges += 1

    @staticmethod
    def addToHistory(undoFuncHandle, undoFuncParam, redoFuncHandle, redoFuncParam):
        if History.pointer != -1:
            del History.timeline[0:History.pointer]
            History.pointer = -1

        # Add action to timeline
        History.timeline.insert(0, {"undoFuncHandle":undoFuncHandle, "undoFuncParam":undoFuncParam, "redoFuncHandle":redoFuncHandle, "redoFuncParam":redoFuncParam})

        if len(History.timeline) > History.MAXTIMELINELENGTH:
            del History.timeline[-1]

        History.recentChanges += 1

    @staticmethod
    def removeFromHistory():
        pass
