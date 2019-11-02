# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\ui\preferences_gui.ui'
#
# Created by: PyQt5 UI code generator 5.13.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_PreferencesDialog(object):
    def setupUi(self, PreferencesDialog):
        PreferencesDialog.setObjectName("PreferencesDialog")
        PreferencesDialog.resize(838, 1018)
        self.verticalLayout = QtWidgets.QVBoxLayout(PreferencesDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
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
        self.verticalLayout_3.addLayout(self.formLayout)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.buttonBox = QtWidgets.QDialogButtonBox(PreferencesDialog)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Discard|QtWidgets.QDialogButtonBox.Save)
        self.buttonBox.setCenterButtons(False)
        self.buttonBox.setObjectName("buttonBox")
        self.horizontalLayout_4.addWidget(self.buttonBox)
        self.verticalLayout_3.addLayout(self.horizontalLayout_4)
        self.verticalLayout.addLayout(self.verticalLayout_3)

        self.retranslateUi(PreferencesDialog)
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
