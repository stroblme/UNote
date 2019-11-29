from os import popen

popen('py -m PyQt5.uic.pyuic .\\ui\\unote_gui.ui -o .\\ui\\unote_qt_export.py -x')
popen('py -m PyQt5.uic.pyuic .\\ui\\preferences_gui.ui -o .\\ui\\preferences_qt_export.py -x')
popen('py -m PyQt5.pyrcc.pyrcc_main .\\style\\BreezeStyleSheets\\breeze.qrc -o .\\style\\BreezeStyleSheets\\breeze_resources.py')
popen('py -m PyQt5.pyrcc.pyrcc_main  .\\assets.qrc -o .\\assets.py')