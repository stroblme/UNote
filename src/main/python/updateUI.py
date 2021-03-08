from os import popen
import subprocess

popen('pyside2-uic .\\ui\\unote_gui.ui -o .\\unote_qt_export.py')
popen('pyside2-uic .\\ui\\preferences_gui.ui -o .\\preferences_qt_export.py')

subprocess.Popen([r"X:\\SSG - Style Sheet Generator\\src\\dist\\ssg\\ssg.exe", "-t", r"X:\\SSG - Style Sheet Generator\\src\\dist\\ssg\\resources\\dark.template", "-p","X:\\UNote\\src\\main\\python\\style\\palette_dark.txt", "-o", "X:\\UNote\\src\\main\\python\\style\\BreezeStyleSheets\\dark.qss"])

subprocess.Popen([r"X:\\SSG - Style Sheet Generator\\src\\dist\\ssg\\ssg.exe", "-t", r"X:\\SSG - Style Sheet Generator\\src\\dist\\ssg\\resources\\light.template", "-p","X:\\UNote\\src\\main\\python\\style\\palette_light.txt", "-o", "X:\\UNote\\src\\main\\python\\style\\BreezeStyleSheets\\light.qss"])

popen('pyside2-rcc .\\style\\BreezeStyleSheets\\breeze.qrc -o .\\style\\BreezeStyleSheets\\breeze_resources.py')
popen('pyside2-rcc .\\assets.qrc -o .\\assets.py')