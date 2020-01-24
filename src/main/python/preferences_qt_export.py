# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'preferences_gui.ui'
##
## Created by: Qt User Interface Compiler version 5.14.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import (QCoreApplication, QMetaObject, QObject, QPoint,
    QRect, QSize, QUrl, Qt)
from PySide2.QtGui import (QBrush, QColor, QConicalGradient, QFont,
    QFontDatabase, QIcon, QLinearGradient, QPalette, QPainter, QPixmap,
    QRadialGradient)
from PySide2.QtWidgets import *

class Ui_PreferencesDialog(object):
    def setupUi(self, PreferencesDialog):
        if PreferencesDialog.objectName():
            PreferencesDialog.setObjectName(u"PreferencesDialog")
        PreferencesDialog.resize(656, 329)
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(PreferencesDialog.sizePolicy().hasHeightForWidth())
        PreferencesDialog.setSizePolicy(sizePolicy)
        self.verticalLayout = QVBoxLayout(PreferencesDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.centralwidget = QWidget(PreferencesDialog)
        self.centralwidget.setObjectName(u"centralwidget")
        self.layoutWidget = QWidget(self.centralwidget)
        self.layoutWidget.setObjectName(u"layoutWidget")
        self.layoutWidget.setGeometry(QRect(10, 10, 618, 291))
        self.verticalLayout_3 = QVBoxLayout(self.layoutWidget)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label = QLabel(self.layoutWidget)
        self.label.setObjectName(u"label")
        font = QFont()
        font.setPointSize(14)
        self.label.setFont(font)

        self.horizontalLayout.addWidget(self.label)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.pushButtonOk = QPushButton(self.layoutWidget)
        self.pushButtonOk.setObjectName(u"pushButtonOk")

        self.horizontalLayout.addWidget(self.pushButtonOk)

        self.pushButtonCancel = QPushButton(self.layoutWidget)
        self.pushButtonCancel.setObjectName(u"pushButtonCancel")

        self.horizontalLayout.addWidget(self.pushButtonCancel)


        self.verticalLayout_3.addLayout(self.horizontalLayout)

        self.verticalSpacer_2 = QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Fixed)

        self.verticalLayout_3.addItem(self.verticalSpacer_2)

        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(u"formLayout")
        self.formLayout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        self.horizontalGroupBox = QGroupBox(self.layoutWidget)
        self.horizontalGroupBox.setObjectName(u"horizontalGroupBox")
        sizePolicy.setHeightForWidth(self.horizontalGroupBox.sizePolicy().hasHeightForWidth())
        self.horizontalGroupBox.setSizePolicy(sizePolicy)
        self.horizontalLayout_2 = QHBoxLayout(self.horizontalGroupBox)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.labelAutosave = QLabel(self.horizontalGroupBox)
        self.labelAutosave.setObjectName(u"labelAutosave")

        self.horizontalLayout_2.addWidget(self.labelAutosave)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.radioButtonSaveOnExit = QRadioButton(self.horizontalGroupBox)
        self.radioButtonSaveOnExit.setObjectName(u"radioButtonSaveOnExit")

        self.horizontalLayout_5.addWidget(self.radioButtonSaveOnExit)

        self.comboBoxAutosaveMode = QComboBox(self.horizontalGroupBox)
        self.comboBoxAutosaveMode.setObjectName(u"comboBoxAutosaveMode")

        self.horizontalLayout_5.addWidget(self.comboBoxAutosaveMode)


        self.horizontalLayout_2.addLayout(self.horizontalLayout_5)


        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.horizontalGroupBox)

        self.horizontalGroupBox1 = QGroupBox(self.layoutWidget)
        self.horizontalGroupBox1.setObjectName(u"horizontalGroupBox1")
        self.horizontalLayout_3 = QHBoxLayout(self.horizontalGroupBox1)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.labelTheme = QLabel(self.horizontalGroupBox1)
        self.labelTheme.setObjectName(u"labelTheme")

        self.horizontalLayout_3.addWidget(self.labelTheme)

        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.radioButtonAffectsPDF = QRadioButton(self.horizontalGroupBox1)
        self.radioButtonAffectsPDF.setObjectName(u"radioButtonAffectsPDF")
        self.radioButtonAffectsPDF.setChecked(False)

        self.horizontalLayout_7.addWidget(self.radioButtonAffectsPDF)

        self.comboBoxThemeSelect = QComboBox(self.horizontalGroupBox1)
        self.comboBoxThemeSelect.setObjectName(u"comboBoxThemeSelect")

        self.horizontalLayout_7.addWidget(self.comboBoxThemeSelect)


        self.horizontalLayout_3.addLayout(self.horizontalLayout_7)


        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.horizontalGroupBox1)

        self.horizontalGroupBox2 = QGroupBox(self.layoutWidget)
        self.horizontalGroupBox2.setObjectName(u"horizontalGroupBox2")
        sizePolicy.setHeightForWidth(self.horizontalGroupBox2.sizePolicy().hasHeightForWidth())
        self.horizontalGroupBox2.setSizePolicy(sizePolicy)
        self.horizontalLayout_4 = QHBoxLayout(self.horizontalGroupBox2)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.labelPenDraw = QLabel(self.horizontalGroupBox2)
        self.labelPenDraw.setObjectName(u"labelPenDraw")

        self.horizontalLayout_4.addWidget(self.labelPenDraw)

        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.radioButtonPenDrawOnly = QRadioButton(self.horizontalGroupBox2)
        self.radioButtonPenDrawOnly.setObjectName(u"radioButtonPenDrawOnly")
        self.radioButtonPenDrawOnly.setChecked(True)

        self.horizontalLayout_6.addWidget(self.radioButtonPenDrawOnly)

        self.comboBoxDrawingMode = QComboBox(self.horizontalGroupBox2)
        self.comboBoxDrawingMode.setObjectName(u"comboBoxDrawingMode")

        self.horizontalLayout_6.addWidget(self.comboBoxDrawingMode)


        self.horizontalLayout_4.addLayout(self.horizontalLayout_6)


        self.formLayout.setWidget(2, QFormLayout.FieldRole, self.horizontalGroupBox2)


        self.verticalLayout_3.addLayout(self.formLayout)


        self.verticalLayout.addWidget(self.centralwidget)


        self.retranslateUi(PreferencesDialog)

        QMetaObject.connectSlotsByName(PreferencesDialog)
    # setupUi

    def retranslateUi(self, PreferencesDialog):
        PreferencesDialog.setWindowTitle(QCoreApplication.translate("PreferencesDialog", u"UNote - Preferences", None))
        self.label.setText(QCoreApplication.translate("PreferencesDialog", u"Preferences", None))
        self.pushButtonOk.setText(QCoreApplication.translate("PreferencesDialog", u"Ok", None))
        self.pushButtonCancel.setText(QCoreApplication.translate("PreferencesDialog", u"Cancel", None))
        self.horizontalGroupBox.setTitle("")
        self.labelAutosave.setText(QCoreApplication.translate("PreferencesDialog", u"Save", None))
        self.radioButtonSaveOnExit.setText(QCoreApplication.translate("PreferencesDialog", u"Save On Exit", None))
        self.labelTheme.setText(QCoreApplication.translate("PreferencesDialog", u"Theme", None))
        self.radioButtonAffectsPDF.setText(QCoreApplication.translate("PreferencesDialog", u"Affects PDF", None))
        self.labelPenDraw.setText(QCoreApplication.translate("PreferencesDialog", u"Drawing", None))
        self.radioButtonPenDrawOnly.setText(QCoreApplication.translate("PreferencesDialog", u"Pen Draw Only", None))
    # retranslateUi

