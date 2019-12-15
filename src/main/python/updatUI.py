from os import popen
import subprocess

popen('py -m PyQt5.uic.pyuic .\\ui\\unote_gui.ui -o .\\unote_qt_export.py -x')
popen('py -m PyQt5.uic.pyuic .\\ui\\preferences_gui.ui -o .\\preferences_qt_export.py -x')

subprocess.Popen([r"X:\\SSG - Style Sheet Generator\\src\\dist\\ssg\\ssg.exe", "-t", r"X:\\SSG - Style Sheet Generator\\src\\dist\\ssg\\resources\\dark.template", "-p","X:\\UNote\\src\\main\\python\\style\\palette_dark.txt", "-o", "X:\\UNote\\src\\main\\python\\style\\BreezeStyleSheets\\dark.qss"])

subprocess.Popen([r"X:\\SSG - Style Sheet Generator\\src\\dist\\ssg\\ssg.exe", "-t", r"X:\\SSG - Style Sheet Generator\\src\\dist\\ssg\\resources\\light.template", "-p","X:\\UNote\\src\\main\\python\\style\\palette_light.txt", "-o", "X:\\UNote\\src\\main\\python\\style\\BreezeStyleSheets\\light.qss"])

popen('pyrcc5 .\\style\\BreezeStyleSheets\\breeze.qrc -o .\\style\\BreezeStyleSheets\\breeze_resources.py')
popen('pyrcc5  .\\assets.qrc -o .\\assets.py')