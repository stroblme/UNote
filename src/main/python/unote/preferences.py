# ---------------------------------------------------------------
# -- CXP Test GUI Preferences File --
#
# Stores the global application preferences
#
# Author: Melvin Strobl
# ---------------------------------------------------------------

from collections import OrderedDict

class Preferences():
    data = OrderedDict()    

    @staticmethod
    def syncPreferences(preferences):
        Preferences.data = preferences

        return Preferences.data

    @staticmethod
    def updateKeyValue(key, value):
        Preferences.data[key] = value

        return Preferences.data[key]