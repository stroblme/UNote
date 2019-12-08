from os import popen

popen('py -m PyQt5.uic.pyuic .\\ui\\unote_gui.ui -o .\\unote_qt_export.py -x')
popen('py -m PyQt5.uic.pyuic .\\ui\\preferences_gui.ui -o .\\preferences_qt_export.py -x')

popen('X:\\SSG - Style Sheet Generator\\src\\dist\\ssg\\ssg.exe -t X:\\SSG - Style Sheet Generator\\src\\dist\\ssg\\resources\\dark.template -p .\\style\\palette.txt -o .\\style\\BreezeStyleSheets\\dark.qss')

popen('pyrcc5 .\\style\\BreezeStyleSheets\\breeze.qrc -o .\\style\\BreezeStyleSheets\\breeze_resources.py')
popen('pyrcc5  .\\assets.qrc -o .\\assets.py')