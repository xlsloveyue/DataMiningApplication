# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'SQL_UI.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_SQL(object):
    def setupUi(self, SQL):
        SQL.setObjectName("SQL")
        SQL.resize(387, 310)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(SQL)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem = QtWidgets.QSpacerItem(78, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.label = QtWidgets.QLabel(SQL)
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.horizontalLayout_2.addWidget(self.label)
        spacerItem1 = QtWidgets.QSpacerItem(88, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        spacerItem2 = QtWidgets.QSpacerItem(20, 18, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem2)
        self.plainTextEdit_sql = QtWidgets.QPlainTextEdit(SQL)
        self.plainTextEdit_sql.setFrameShape(QtWidgets.QFrame.WinPanel)
        self.plainTextEdit_sql.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.plainTextEdit_sql.setLineWidth(4)
        self.plainTextEdit_sql.setMidLineWidth(0)
        self.plainTextEdit_sql.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.plainTextEdit_sql.setTabChangesFocus(False)
        self.plainTextEdit_sql.setOverwriteMode(True)
        self.plainTextEdit_sql.setTabStopWidth(81)
        self.plainTextEdit_sql.setCursorWidth(1)
        self.plainTextEdit_sql.setMaximumBlockCount(6)
        self.plainTextEdit_sql.setObjectName("plainTextEdit_sql")
        self.verticalLayout.addWidget(self.plainTextEdit_sql)
        spacerItem3 = QtWidgets.QSpacerItem(17, 17, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem3)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem4 = QtWidgets.QSpacerItem(48, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem4)
        self.pushButton_sqlconfirm = QtWidgets.QPushButton(SQL)
        self.pushButton_sqlconfirm.setObjectName("pushButton_sqlconfirm")
        self.horizontalLayout.addWidget(self.pushButton_sqlconfirm)
        spacerItem5 = QtWidgets.QSpacerItem(138, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem5)
        self.pushButton_sqlcancel = QtWidgets.QPushButton(SQL)
        self.pushButton_sqlcancel.setObjectName("pushButton_sqlcancel")
        self.horizontalLayout.addWidget(self.pushButton_sqlcancel)
        spacerItem6 = QtWidgets.QSpacerItem(48, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem6)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.verticalLayout_2.addLayout(self.verticalLayout)

        self.retranslateUi(SQL)
        QtCore.QMetaObject.connectSlotsByName(SQL)

    def retranslateUi(self, SQL):
        _translate = QtCore.QCoreApplication.translate
        SQL.setWindowTitle(_translate("SQL", "Form"))
        self.label.setText(_translate("SQL", "请输入需要使用的SQL语句"))
        self.plainTextEdit_sql.setPlainText(_translate("SQL", "select * from "))
        self.pushButton_sqlconfirm.setText(_translate("SQL", "确认"))
        self.pushButton_sqlcancel.setText(_translate("SQL", "取消"))
