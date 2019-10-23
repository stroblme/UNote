# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\ui\preferences_gui.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_PreferencesDialog(object):
    def setupUi(self, PreferencesDialog):
        PreferencesDialog.setObjectName("PreferencesDialog")
        PreferencesDialog.resize(838, 1018)
        self.verticalLayout = QtWidgets.QVBoxLayout(PreferencesDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.labelAppearance = QtWidgets.QLabel(PreferencesDialog)
        font = QtGui.QFont()
        font.setPointSize(9)
        self.labelAppearance.setFont(font)
        self.labelAppearance.setObjectName("labelAppearance")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.labelAppearance)
        self.groupBoxThemeSwitch = QtWidgets.QGroupBox(PreferencesDialog)
        self.groupBoxThemeSwitch.setMinimumSize(QtCore.QSize(0, 30))
        self.groupBoxThemeSwitch.setTitle("")
        self.groupBoxThemeSwitch.setObjectName("groupBoxThemeSwitch")
        self.horizontalLayoutWidget = QtWidgets.QWidget(self.groupBoxThemeSwitch)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(0, 0, 531, 31))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.horizontalLayoutThemeSwitch = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayoutThemeSwitch.setSizeConstraint(QtWidgets.QLayout.SetMaximumSize)
        self.horizontalLayoutThemeSwitch.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayoutThemeSwitch.setObjectName("horizontalLayoutThemeSwitch")
        self.radioButtonDarkTheme = QtWidgets.QRadioButton(self.horizontalLayoutWidget)
        self.radioButtonDarkTheme.setChecked(False)
        self.radioButtonDarkTheme.setObjectName("radioButtonDarkTheme")
        self.horizontalLayoutThemeSwitch.addWidget(self.radioButtonDarkTheme)
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.groupBoxThemeSwitch)
        self.verticalLayout.addLayout(self.formLayout)
        self.buttonBox = QtWidgets.QDialogButtonBox(PreferencesDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(PreferencesDialog)
        self.buttonBox.accepted.connect(PreferencesDialog.accept)
        self.buttonBox.rejected.connect(PreferencesDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(PreferencesDialog)

    def retranslateUi(self, PreferencesDialog):
        _translate = QtCore.QCoreApplication.translate
        PreferencesDialog.setWindowTitle(_translate("PreferencesDialog", "Dialog"))
        self.labelAppearance.setText(_translate("PreferencesDialog", "Appearance"))
        self.radioButtonDarkTheme.setText(_translate("PreferencesDialog", "Dark Theme"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    PreferencesDialog = QtWidgets.QDialog()
    ui = Ui_PreferencesDialog()
    ui.setupUi(PreferencesDialog)
    PreferencesDialog.show()
    sys.exit(app.exec_())
