import sys
from indexed import IndexedOrderedDict

class History():

    timeline = IndexedOrderedDict()
    pointer = 0 # Latest pointer

    def __init__(self):
        pass

    def undo(self):
        # Go back in time
        self.pointer -= 1

        action = self.timeline[self.pointer]

        action["undoFuncHandle"](action["undoFuncParam"])

    def redo(self):
        # Go back in time
        self.pointer += 1

        action = self.timeline[self.pointer]

        action["undoFuncHandle"](action["undoFuncParam"])

    def addToHistory(self, undoFuncHandle, undoFuncParam):
        action = {"undoFuncHandle":undoFuncHandle, "undoFuncParam":undoFuncParam}

        # Add action to timeline
        self.timeline[self.pointer] = action
        # Increment timeline
        self.pointer += 1

    def removeFromHistory(self):
        pass
