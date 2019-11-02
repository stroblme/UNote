from os import popen

popen('python -m PyQt5.uic.pyuic .\\ui\\unote_gui.ui -o .\\ui\\unote_qt_export.py -x')
popen('py -3 -m PyQt5.uic.pyuic .\\ui\\preferences_gui.ui -o .\\ui\\preferences_qt_export.py -x')
popen('pyrcc5 .\\style\\BreezeStyleSheets\\breeze.qrc -o .\\style\\BreezeStyleSheets\\breeze_resources.py')
popen('pyrcc5 .\\assets.qrc -o .\\assets.py')