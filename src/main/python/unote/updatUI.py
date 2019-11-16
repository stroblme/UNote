from os import popen

popen('python -m PyQt5.uic.pyuic .\\ui\\unote_gui.ui -o .\\ui\\unote_qt_export.py -x')
popen('python -m PyQt5.uic.pyuic .\\ui\\preferences_gui.ui -o .\\ui\\preferences_qt_export.py -x')
popen('pyrcc5.exe .\\style\\BreezeStyleSheets\\breeze.qrc -o .\\style\\BreezeStyleSheets\\breeze_resources.py')
popen('pyrcc5.exe  .\\assets.qrc -o .\\assets.py')