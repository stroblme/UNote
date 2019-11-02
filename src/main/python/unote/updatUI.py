import subprocess

subprocess.run('py -3 -m PyQt5.uic.pyuic .\\ui\\unote_gui.ui -o .\\ui\\unote_qt_export.py -x')
subprocess.run('py -3 -m PyQt5.uic.pyuic .\\ui\\preferences_gui.ui -o .\\ui\\preferences_qt_export.py -x')
subprocess.run('pyrcc5 .\\style\\BreezeStyleSheets\\breeze.qrc -o .\\style\\BreezeStyleSheets\\breeze_resources.py')
subprocess.run('pyrcc5 .\\assets.qrc -o .\\assets.py')