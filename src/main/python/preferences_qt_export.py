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
        PreferencesDialog.resize(688, 365)
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
        self.layoutWidget.setGeometry(QRect(10, 10, 647, 318))
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
        self.horizontalGroupBoxSaveSettings = QGroupBox(self.layoutWidget)
        self.horizontalGroupBoxSaveSettings.setObjectName(u"horizontalGroupBoxSaveSettings")
        sizePolicy.setHeightForWidth(self.horizontalGroupBoxSaveSettings.sizePolicy().hasHeightForWidth())
        self.horizontalGroupBoxSaveSettings.setSizePolicy(sizePolicy)
        self.horizontalLayout_2 = QHBoxLayout(self.horizontalGroupBoxSaveSettings)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.labelAutosave = QLabel(self.horizontalGroupBoxSaveSettings)
        self.labelAutosave.setObjectName(u"labelAutosave")

        self.horizontalLayout_2.addWidget(self.labelAutosave)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.radioButtonSaveOnExit = QRadioButton(self.horizontalGroupBoxSaveSettings)
        self.radioButtonSaveOnExit.setObjectName(u"radioButtonSaveOnExit")

        self.horizontalLayout_5.addWidget(self.radioButtonSaveOnExit)

        self.comboBoxAutosaveMode = QComboBox(self.horizontalGroupBoxSaveSettings)
        self.comboBoxAutosaveMode.setObjectName(u"comboBoxAutosaveMode")

        self.horizontalLayout_5.addWidget(self.comboBoxAutosaveMode)


        self.horizontalLayout_2.addLayout(self.horizontalLayout_5)


        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.horizontalGroupBoxSaveSettings)

        self.horizontalGroupBoxThemeSettings = QGroupBox(self.layoutWidget)
        self.horizontalGroupBoxThemeSettings.setObjectName(u"horizontalGroupBoxThemeSettings")
        self.horizontalLayout_3 = QHBoxLayout(self.horizontalGroupBoxThemeSettings)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.labelTheme = QLabel(self.horizontalGroupBoxThemeSettings)
        self.labelTheme.setObjectName(u"labelTheme")

        self.horizontalLayout_3.addWidget(self.labelTheme)

        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.radioButtonAffectsPDF = QRadioButton(self.horizontalGroupBoxThemeSettings)
        self.radioButtonAffectsPDF.setObjectName(u"radioButtonAffectsPDF")
        self.radioButtonAffectsPDF.setChecked(False)

        self.horizontalLayout_7.addWidget(self.radioButtonAffectsPDF)

        self.comboBoxThemeSelect = QComboBox(self.horizontalGroupBoxThemeSettings)
        self.comboBoxThemeSelect.setObjectName(u"comboBoxThemeSelect")

        self.horizontalLayout_7.addWidget(self.comboBoxThemeSelect)


        self.horizontalLayout_3.addLayout(self.horizontalLayout_7)


        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.horizontalGroupBoxThemeSettings)

        self.horizontalGroupBoxDrawingSettings = QGroupBox(self.layoutWidget)
        self.horizontalGroupBoxDrawingSettings.setObjectName(u"horizontalGroupBoxDrawingSettings")
        sizePolicy.setHeightForWidth(self.horizontalGroupBoxDrawingSettings.sizePolicy().hasHeightForWidth())
        self.horizontalGroupBoxDrawingSettings.setSizePolicy(sizePolicy)
        self.horizontalLayout_4 = QHBoxLayout(self.horizontalGroupBoxDrawingSettings)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.labelPenDraw = QLabel(self.horizontalGroupBoxDrawingSettings)
        self.labelPenDraw.setObjectName(u"labelPenDraw")

        self.horizontalLayout_4.addWidget(self.labelPenDraw)

        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.radioButtonPenDrawOnly = QRadioButton(self.horizontalGroupBoxDrawingSettings)
        self.radioButtonPenDrawOnly.setObjectName(u"radioButtonPenDrawOnly")
        self.radioButtonPenDrawOnly.setChecked(False)

        self.horizontalLayout_6.addWidget(self.radioButtonPenDrawOnly)

        self.comboBoxDrawingMode = QComboBox(self.horizontalGroupBoxDrawingSettings)
        self.comboBoxDrawingMode.setObjectName(u"comboBoxDrawingMode")

        self.horizontalLayout_6.addWidget(self.comboBoxDrawingMode)


        self.horizontalLayout_4.addLayout(self.horizontalLayout_6)


        self.formLayout.setWidget(2, QFormLayout.FieldRole, self.horizontalGroupBoxDrawingSettings)

        self.horizontalGroupBoxToolboxSettings = QGroupBox(self.layoutWidget)
        self.horizontalGroupBoxToolboxSettings.setObjectName(u"horizontalGroupBoxToolboxSettings")
        sizePolicy.setHeightForWidth(self.horizontalGroupBoxToolboxSettings.sizePolicy().hasHeightForWidth())
        self.horizontalGroupBoxToolboxSettings.setSizePolicy(sizePolicy)
        self.horizontalLayout_8 = QHBoxLayout(self.horizontalGroupBoxToolboxSettings)
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.labelToolBox = QLabel(self.horizontalGroupBoxToolboxSettings)
        self.labelToolBox.setObjectName(u"labelToolBox")

        self.horizontalLayout_8.addWidget(self.labelToolBox)

        self.horizontalLayout_9 = QHBoxLayout()
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.radioButtonUsePenAsDefault = QRadioButton(self.horizontalGroupBoxToolboxSettings)
        self.radioButtonUsePenAsDefault.setObjectName(u"radioButtonUsePenAsDefault")
        self.radioButtonUsePenAsDefault.setChecked(False)

        self.horizontalLayout_9.addWidget(self.radioButtonUsePenAsDefault)

        self.radioButtonToolboxFollowsEdit = QRadioButton(self.horizontalGroupBoxToolboxSettings)
        self.radioButtonToolboxFollowsEdit.setObjectName(u"radioButtonToolboxFollowsEdit")
        self.radioButtonToolboxFollowsEdit.setChecked(True)

        self.horizontalLayout_9.addWidget(self.radioButtonToolboxFollowsEdit)


        self.horizontalLayout_8.addLayout(self.horizontalLayout_9)


        self.formLayout.setWidget(3, QFormLayout.FieldRole, self.horizontalGroupBoxToolboxSettings)

        self.horizontalGroupBoxToolboxSettings_2 = QGroupBox(self.layoutWidget)
        self.horizontalGroupBoxToolboxSettings_2.setObjectName(u"horizontalGroupBoxToolboxSettings_2")
        sizePolicy.setHeightForWidth(self.horizontalGroupBoxToolboxSettings_2.sizePolicy().hasHeightForWidth())
        self.horizontalGroupBoxToolboxSettings_2.setSizePolicy(sizePolicy)
        self.horizontalLayout_10 = QHBoxLayout(self.horizontalGroupBoxToolboxSettings_2)
        self.horizontalLayout_10.setObjectName(u"horizontalLayout_10")
        self.labelToolBox_2 = QLabel(self.horizontalGroupBoxToolboxSettings_2)
        self.labelToolBox_2.setObjectName(u"labelToolBox_2")

        self.horizontalLayout_10.addWidget(self.labelToolBox_2)

        self.horizontalLayout_11 = QHBoxLayout()
        self.horizontalLayout_11.setObjectName(u"horizontalLayout_11")
        self.radioButtonNoInteractionWhileEditing = QRadioButton(self.horizontalGroupBoxToolboxSettings_2)
        self.radioButtonNoInteractionWhileEditing.setObjectName(u"radioButtonNoInteractionWhileEditing")
        self.radioButtonNoInteractionWhileEditing.setChecked(False)

        self.horizontalLayout_11.addWidget(self.radioButtonNoInteractionWhileEditing)


        self.horizontalLayout_10.addLayout(self.horizontalLayout_11)


        self.formLayout.setWidget(4, QFormLayout.FieldRole, self.horizontalGroupBoxToolboxSettings_2)


        self.verticalLayout_3.addLayout(self.formLayout)


        self.verticalLayout.addWidget(self.centralwidget)


        self.retranslateUi(PreferencesDialog)

        QMetaObject.connectSlotsByName(PreferencesDialog)
    # setupUi

    def retranslateUi(self, PreferencesDialog):
        PreferencesDialog.setWindowTitle(QCoreApplication.translate("PreferencesDialog", u"UNote - Preferences", None))
        self.label.setText(QCoreApplication.translate("PreferencesDialog", u"Preferences", None))
        self.pushButtonOk.setText(QCoreApplication.translate("PreferencesDialog", u"Ok", None))
#if QT_CONFIG(shortcut)
        self.pushButtonOk.setShortcut(QCoreApplication.translate("PreferencesDialog", u"Return", None))
#endif // QT_CONFIG(shortcut)
        self.pushButtonCancel.setText(QCoreApplication.translate("PreferencesDialog", u"Cancel", None))
#if QT_CONFIG(shortcut)
        self.pushButtonCancel.setShortcut(QCoreApplication.translate("PreferencesDialog", u"Esc", None))
#endif // QT_CONFIG(shortcut)
        self.horizontalGroupBoxSaveSettings.setTitle("")
        self.labelAutosave.setText(QCoreApplication.translate("PreferencesDialog", u"Save", None))
        self.radioButtonSaveOnExit.setText(QCoreApplication.translate("PreferencesDialog", u"Save On Exit", None))
        self.labelTheme.setText(QCoreApplication.translate("PreferencesDialog", u"Theme", None))
        self.radioButtonAffectsPDF.setText(QCoreApplication.translate("PreferencesDialog", u"Affects PDF", None))
        self.labelPenDraw.setText(QCoreApplication.translate("PreferencesDialog", u"Drawing", None))
        self.radioButtonPenDrawOnly.setText(QCoreApplication.translate("PreferencesDialog", u"Pen Draw Only", None))
        self.labelToolBox.setText(QCoreApplication.translate("PreferencesDialog", u"Toolbox", None))
#if QT_CONFIG(tooltip)
        self.radioButtonUsePenAsDefault.setToolTip(QCoreApplication.translate("PreferencesDialog", u"Show only relevant tools. E.g. in tablet mode, a Text Box is not relevant.", None))
#endif // QT_CONFIG(tooltip)
        self.radioButtonUsePenAsDefault.setText(QCoreApplication.translate("PreferencesDialog", u"Use Pen As Default", None))
#if QT_CONFIG(tooltip)
        self.radioButtonToolboxFollowsEdit.setToolTip(QCoreApplication.translate("PreferencesDialog", u"Show only relevant tools. E.g. in tablet mode, a Text Box is not relevant.", None))
#endif // QT_CONFIG(tooltip)
        self.radioButtonToolboxFollowsEdit.setText(QCoreApplication.translate("PreferencesDialog", u"Reduced Toolbar", None))
        self.labelToolBox_2.setText(QCoreApplication.translate("PreferencesDialog", u"Interactuin", None))
#if QT_CONFIG(tooltip)
        self.radioButtonNoInteractionWhileEditing.setToolTip(QCoreApplication.translate("PreferencesDialog", u"Show only relevant tools. E.g. in tablet mode, a Text Box is not relevant.", None))
#endif // QT_CONFIG(tooltip)
        self.radioButtonNoInteractionWhileEditing.setText(QCoreApplication.translate("PreferencesDialog", u"No interaction while editing", None))
    # retranslateUi

