from PyQt5 import QtGui
from PyQt5.QtWidgets import QMessageBox,QFileDialog,QInputDialog,QLineEdit
from MainWindow import Ui_MainWindow
from 数据库登录 import Ui_Form
import sys
import pandas as pd
import MySQLdb
import sqlite3
from PyQt5.QtCore import QThread,pyqtSignal,QUrl
from qtpandas.models.DataFrameModel import DataFrameModel
from warnings import simplefilter
from SQL_UI import Ui_SQL
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtWidgets import QVBoxLayout, QSizePolicy, QWidget
from PyQt5 import QtWidgets,QtCore
from PyQt5.QtWidgets import QMainWindow
from pyecharts import options as opts
from pyecharts.charts import Bar, Page


simplefilter(action='ignore', category=FutureWarning)  #避免报FutureWarning错误
'''
存在问题：
       1. 打开文件窗口不选择关闭，直接关闭打开文件窗口，在文件名不存在的情况下，读取线程依旧进行，信号showdata_signal依旧发送，浪费了计算机资源
'''


fileName = ''
data = pd.DataFrame(None)
data_orignal = pd.DataFrame(None)
selectedFliter = ''
fileNameSave = ''
selectedfliterSave = ''
standard_data = pd.DataFrame(None)    #用于数据的标准化处理
standard = ''  #数据标准化的规则
databaseUserInformation = ['localhost','root','*****','database']  #0:Host  1:User  2:Password 3：database
sql = ''
table_name = 'new_table'  #保存的数据库的表格默认名称
pyechartsdata = pd.DataFrame(None)
attribute_name = ''#指定属性的名称
class MainWindows(QMainWindow,Ui_MainWindow):
    global fileName,selectedFliter,data,data_orignal,sql,table_name,standard_data,standard,pyechartsdata

    '''信号定义'''
    readdatabase_signal = pyqtSignal()
    showsql_signal = pyqtSignal(int)  #sql界面显示信号
    confirmsql_signal = pyqtSignal(int) #sql界面确认信号
    cleardatashow_signal = pyqtSignal()#清空所显示的数据信号
    attributes_changed_datashow_signal = pyqtSignal()
    comboBox_content_signal = pyqtSignal(list)
    attributesmodel_changed_datashow_signal = pyqtSignal(pd.DataFrame)#当选择属性发生改变时，显示属性表格需要接受的信号
    showmatplotlib_signal = pyqtSignal() #用来描绘视图的信号


    '''初始化'''
    def __init__(self):
        super(MainWindows,self).__init__()
        self.setupUi(self)
        self.setWindowTitle('数据挖掘')
        self.browser = QWebEngineView()
        # 加载外部的web界面
        self.gridLayout_pciture.addWidget(self.browser)

        '''信号与槽的连接'''
        self.pushButton_openfile.clicked.connect(self.preprocess_openfile)#打开文件按钮点击槽函数的连接
        #self.showdata_signal.connect(self.showdata)  #显示数据槽函数的连接
        self.pushButton_save.clicked.connect(self.savedata) #保存文件按钮点击槽函数的连接
        self.pushButton_datareturn.clicked.connect(self.datareturn_orginal)
        self.pushButton_opendatabase.clicked.connect(self.onclicked_sqlbutton_way_0)
        self.readdatabase_signal.connect(self.preprocess_openfile)
        self.pushButton_sqllanguage.clicked.connect(self.onclicked_sqlbutton_way_1)
        self.showsql_signal.connect(self.onclicked_sqlbutton)
        self.confirmsql_signal.connect(self.ConfirmSQLInformation)
        self.pushButton_logdatabase.clicked.connect(self.opendatabase)
        self.pushButton_cleardata.clicked.connect(self.ClearData)
        self.cleardatashow_signal.connect(self.ClearDatashow)
        self.pushButton_view.clicked.connect(self.showpyecharts)    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!需要更改
        self.comboBox_attributes.currentTextChanged.connect(self.comboBox_content_changed)
        self.attributesmodel_changed_datashow_signal.connect(self.showAttributesData)
        self.pushButton_queding1.clicked.connect(self.comBoBox_content)
        self.comboBox_content_signal.connect(self.comboBox_content)
        self.attributes_changed_datashow_signal.connect(self.attributes_data_show)
        #单选按钮的信号连接
        self.radioButton_Zscore.clicked.connect(self.radiobutton_clicked_standard)#单选按钮的信号连接
        self.radioButton_xiaoshudingbiao.clicked.connect(self.radiobutton_clicked_standard)
        self.radioButton_Minmax.clicked.connect(self.radiobutton_clicked_standard)
        #读取线程中的信号连接
        self.readthread = ReadThread()    #读取线程中对象的声明
        self.readthread.sendException_signal.connect(self.Warning_QMessageBox)#读取线程中的信号连接
        self.readthread.showdata_signal.connect(self.showdata)
        self.readthread.radiobutton_signal.connect(self.radiobutton_clicked_standard)
        self.readthread.comboBox_signal.connect(self.comboBox_content)
        #保存线程中的信号连接
        self.savethread = SaveThread()
        self.savethread.sendSaveException_signal.connect(self.Warning_QMessageBox)
        #标准化数据线程中的信号连接
        self.standarddatathread = StandardDataThread()
        self.standarddatathread.standardException_signal.connect(self.Warning_QMessageBox)

        #描绘视图的信号链接
        #self.showmatplotlib_signal.connect(self.showMatplotlib)
        #pyecahrts线程信号的连接
        self.pyechartsthread = pyechartsThread()
        self.pyechartsthread.show_pyecharts_signal.connect(self.showAttributesData)



        '''图标设置'''
        self.setWindowIcon(QtGui.QIcon('Picture/主窗口图标.png'))


        '''----------任务栏预先设置-----------'''
        self.statusBar().setStyleSheet("QStatusBar::item{border:0px}") #去掉任务栏
        self.label_status = QtWidgets.QLabel()
        self.label_status.setMinimumSize(QtCore.QSize(20,10))
        self.statusBar().addPermanentWidget(self.label_status,1)#将lable_status标签加入任务栏
        self.label_status.setText("欢迎使用本程序")

        #预处理界面按钮的设置

        self.pushButton_openfile.setToolTip('支持excel,txt,csv文件')
        self.pushButton_opendatabase.setToolTip('打开数据库文件')
        self.pushButton_logdatabase.setToolTip('登录数据库账户')
        self.pushButton_opendatabase.setToolTip('不需要数据库账户的可直接点击此按钮')
        self.pushButton_queding1.setToolTip('当你使用此栏编辑时需要点击确认按钮')

        #指定属性结果框DataTableWidget的按钮隐藏
        self.qtpandas_attributewidget.editButton.hide()
        self.qtpandas_attributewidget.addColumnButton.hide()
        self.qtpandas_attributewidget.addRowButton.hide()
        self.qtpandas_attributewidget.removeColumnButton.hide()
        self.qtpandas_attributewidget.removeRowButton.hide()

        '''#视图初始化
        self.matplotlib = Matplotlibwidget()  # 初始化控件对象
        self.gridLayout_picture.addWidget(self.matplotlib)  # 将控件对象加入到栅格布局中去'''


    def showpyecharts(self):
        try:
            #print('11')
            self.pyechartsthread.start()
            #c.render()
            self.browser.load(QUrl('D:/办公软件/Python源文件/数据挖掘应用/render.html'))  # 本地Html需要使用绝对地址 ，且用‘/’
        except Exception as e:
            self.Warning_QMessageBox(str(e))


    def showdata(self):
        '''初始化pandasqt'''
        global data,data_orignal
        try:
            widget_qtpandas = self.pandastablewidget
            widget_qtpandas.resize(370, 250)
            self.model = DataFrameModel()  # 设置新的模型
            widget_qtpandas.setViewModel(self.model)
            data = pd.DataFrame(data)
            # self.data_orignal = self.data.copy(deep=False)  #浅拷贝,旧地址的内容改变不会改变新地址的内容
            self.model.setDataFrame(data)
            self.label_status.setText('欢迎使用本程序')  # 任务栏显示信息完成
        except Exception as e:
            self.Warning_QMessageBox(str(e))



    def showAttributesData(self,attributes_data):
        '''初始化指定属性显示表格信息的qtpandastablewidget(qtpandas_attributewidget)'''
        global  pyechartsdata
        pyechartsdata = attributes_data
        self.attributes_data = attributes_data
        try:
            attributewidget_qtpandas = self.qtpandas_attributewidget
            self.attributesmodel = DataFrameModel()
            attributewidget_qtpandas.setViewModel(self.attributesmodel)
            self.attributesmodel.setDataFrame(self.attributes_data)
            #self.pyechartsthread.start()
            #self.browser.load(QUrl('D:/办公软件/Python源文件/数据挖掘应用/render.html'))  # 本地Html需要使用绝对地址 ，且用‘/’


            #self.showmatplotlib_signal.emit()  #属性图标显示出来后发送视图显示的信号

        except Exception as e:
            self.Warning_QMessageBox(str(e))




    def savedata(self):
        global fileNameSave,selectedfliterSave,selectedFliter
        try:
            if '.db' not in selectedFliter:
                fileNameSave, selectedfliterSave = QFileDialog.getSaveFileName(
                    self, '保存文件', 'C:/windows',
                    'Excel(*.xlsx);;文本文档(*.txt);;csv文件(*.csv);;数据库文件(*.sqlite);;(*.db);;(*.db3)',
                    None
                )
            if '.db' in selectedFliter:
                self.Input_QInputDialog()
            if fileNameSave!='':
                self.savethread.start()
            else:
                pass
        except Exception as e:
            self.Warning_QMessageBox(str(e))



    '''-----------------------------------按钮只能触发一次数据还原，需改进---------------------------------------'''
    def datareturn_orginal(self): #还原数据
        global data_orignal,data
        try:
            if data.empty:
                self.Information_QMessageBox('空数据')
            else:
                self.model.setDataFrame(data_orignal)
                data = data_orignal.copy()
        except Exception as e:
            self.Warning_QMessageBox(str(e))







    '''
    警告提示框
    content：警告内容
    '''
    def Warning_QMessageBox(self,content):
        warning = QMessageBox.warning(
            self,("警告"),content,
            QMessageBox.StandardButtons(QMessageBox.Retry)
        )

    '''
    信息提示框
    content:提示内容
    '''
    def Information_QMessageBox(self,content):
        information = QMessageBox.information(
            self,'提示',content,
            QMessageBox.StandardButtons(QMessageBox.Ok)
        )

    def Input_QInputDialog(self):
        global table_name
        name,state = QInputDialog.getText(
            self,'数据库保存','新建表格名称',
            QLineEdit.Normal,('new_table')
        )
        if state==True:
            table_name = name
        else:
            pass




    '''----------------主界面中打开按钮响应的槽函数-------------------------------------'''
    def preprocess_openfile(self):
        global fileName, selectedFliter

        fileName, selectedFliter = QFileDialog.getOpenFileName(
            self, '选择文件', 'c:\\windows',
            '数据库文件(*.db);;Excel文件(*.xlsx);;csv文件 (*.csv);;文本文档(*.txt);;数据库文件(*.mdf);;数据库文件(*.sqlite);;数据库文件(*.db3)',
            None
        )
        if fileName!='':
            self.label_status.setText('正在读取数据')
            self.readthread.start()
        else:
            pass



    '''-------------------------主界面中打开数据库按钮相应的槽函数-----------------------'''
    def opendatabase(self):
        global databaseUserInformation
        self.databasewindow = DataBaseWindow()
        self.databasewindow.show()
        self.databasewindow.pushButton_confirm.clicked.connect(self.ConfirmDatabaseInformation)
        self.databasewindow.pushButton_cancel.clicked.connect(self.databasewindow.close)


    '''-----------------数据库登录界面确认按钮响应的槽函数----------------------------'''
    '''!!!!!!!!!!!!!!!!这里还需要加入数据库用户密码数据库名称是否输入正确的判断!!!!!!!!!!!!!!!!!!!'''
    def ConfirmDatabaseInformation(self):
        global databaseUserInformation
        if self.databasewindow.lineEdit_Host.text()!='':
            databaseUserInformation[0] = self.databasewindow.lineEdit_Host.text()  # 获取lineEdit文本框中的内容
        else:
            self.databasewindow.Warning_QMessageBox('Host栏不能为空')
        if self.databasewindow.lineEdit_User.text()!='':
            databaseUserInformation[1] = self.databasewindow.lineEdit_User.text()
        else:
            self.databasewindow.Warning_QMessageBox('User栏不能为空')
        if self.databasewindow.lineEdit_Password.text()!='':
            databaseUserInformation[2] = self.databasewindow.lineEdit_Password.text()
        else:
            self.databasewindow.Warning_QMessageBox('密码不能为空')
        if self.databasewindow.lineEdit_Database.text()!='':
            databaseUserInformation[3] = self.databasewindow.lineEdit_Database.text()
        else:
            self.databasewindow.Warning_QMessageBox('数据库名称不能为空')
        if (self.databasewindow.lineEdit_Host.text()!='' and self.databasewindow.lineEdit_User.text()!=''  and
            self.databasewindow.lineEdit_Password.text()!='' and self.databasewindow.lineEdit_Database.text()!='') :
            self.databasewindow.close()
            '''-------!!!!!账户判断语句！！！！！！！！！！----------'''
            self.Information_QMessageBox('登录成功')




    '''-------------------点击SQL语言按钮相应的槽函数-----------------------------'''
    def onclicked_sqlbutton(self,way):
        '''
        :param way: 0:输入初始sql语句后，打开文件夹选择数据库文件打开
                    1：更新sql语句，对数据重新处理，不打开文件夹选择文件打开
        :return: None
        '''
        self.sqlwindow = SQLWindow()
        self.sqlwindow.show()
        if way==0:
            self.sqlwindow.pushButton_sqlconfirm.clicked.connect(self.ConfirmSQLInformation_0)
        if way==1:
            self.sqlwindow.pushButton_sqlconfirm.clicked.connect(self.ConfirmSqlInformation_1)

        self.sqlwindow.pushButton_sqlcancel.clicked.connect(self.sqlwindow.close)



    def onclicked_sqlbutton_way_1(self):
        global selectedFliter
        if '.db' in selectedFliter:  #！！！！！！！！！！！！！！！！！！！！！！！可以增加
            self.showsql_signal.emit(1)
        else:
            self.Warning_QMessageBox('不是数据库文件')



    def onclicked_sqlbutton_way_0(self):
        self.showsql_signal.emit(0)

    def ConfirmSQLInformation_0(self):
        self.confirmsql_signal.emit(0)

    def ConfirmSqlInformation_1(self):
        self.confirmsql_signal.emit(1)

    '''---------------------SQL界面确认按钮相应的槽函数------------------------------'''
    def ConfirmSQLInformation(self,way):
        '''
        :param way: 0:表示输入sql语句后打开文件
                    1：表示打开文件后修改sql语句
        :return: 全局变量 sql
        '''
        global sql,data,selectedFliter

        if self.sqlwindow.plainTextEdit_sql.toPlainText() != '':
            sql = self.sqlwindow.plainTextEdit_sql.toPlainText()  # plainTextEdit.toPlainText()获取文本框中的文本内容
            if way == 0:
                self.readdatabase_signal.emit()
                self.sqlwindow.close()
            if way == 1:
                if data.empty:  # 注意DataFrame数据结构判断是否为空的方法，若用data!=None也是错误的
                    self.sqlwindow.Warning_QMessageBox('当前未读入任何数据，请先点击打开数据库按钮')
                else:
                    self.readthread.start()
                    self.label_status.setText('正在读取数据')
                    self.sqlwindow.close()
        else:
            self.sqlwindow.Warning_QMessageBox('SQL语句不能为空')
        # print(sql)





    def ClearData(self):
        '''
        清空数据
        '''
        global data,data_orignal,standard_data
        if data.empty:
            self.Information_QMessageBox('已经是空数据')
        else:
            data = pd.DataFrame(None)
            data_orignal = pd.DataFrame(None)
            standard_data = pd.DataFrame(None)
            self.attributes_data = pd.DataFrame(None)
            self.comboBox_attributes.clear()
            self.cleardatashow_signal.emit()
            #self.matplotlib.clear_plot()


    def ClearDatashow(self):
        global data
        self.model.setDataFrame(data)
        self.attributesmodel.setDataFrame(self.attributes_data)



    def radiobutton_clicked_standard(self):
        '''
         数据标准化规则
        '''
        global standard

        if self.radioButton_Minmax.isChecked():
            standard = 'Minmax'
        if self.radioButton_xiaoshudingbiao.isChecked():
            standard = 'xiaoshudingbiao'
        if self.radioButton_Zscore.isChecked():  #标准差标准化
            standard = 'Zscore'
        self.standarddatathread.start()



    def comBoBox_content(self):
        global data
        if data.empty:
            self.Warning_QMessageBox('数据为空')
        else:
            try:
                # print('1111')
                self.comboBox_content_signal.emit(list(data.columns))
                # print(list(data.columns))
            except Exception as e:
                print(str(e))



    def comboBox_content(self,attributes):
        self.comboBox_attributes.clear()#清空之前的下拉列表内容
        self.attributes = attributes
        for i in range(len(self.attributes)):
            self.comboBox_attributes.addItem(self.attributes[i])


    def comboBox_content_changed(self):
        self.label_comboboxattributes.setText(self.comboBox_attributes.currentText())
        if self.comboBox_attributes.currentText()!='':   #判断一下下拉列表框是否为空，因为有清空列表框的操作，会触发值改变的信号的产生
            self.attributes_changed_datashow_signal.emit()
        else:
            pass




    def attributes_data_show(self):
        global data
        try:
            self.attributes_data = data.copy()
            self.attribute_value = self.comboBox_attributes.currentText()
            self.valuecounts = self.attributes_data[self.attribute_value].value_counts()
            self.attributes_data = pd.DataFrame({
                # 'No.': [x for x in range(len(self.valuecounts))],  #当前属性不同标签值的个数
                'Label': [y for y in self.valuecounts.index],
                'Count': [self.valuecounts[z] for z in self.valuecounts.index]
            }
            )
            self.attributesmodel_changed_datashow_signal.emit(self.attributes_data)
        except Exception as e:
            self.Warning_QMessageBox(str(e))



    def showMatplotlib(self):
        try:
            self.X = list(self.attributes_data['Label'])
            self.Y = list(self.attributes_data['Count'])
            self.matplotlib.plot(range(len(self.X)), self.Y)
        except Exception as e:
            self.Warning_QMessageBox(str(e))








class ReadThread(QThread):
    #定义全局变量
    global fileName,selectedFliter,data,data_orignal,databaseUserInformation,sql

    #定义信号
    read_sqlsignal = pyqtSignal()
    showdata_signal = pyqtSignal()
    sendException_signal = pyqtSignal(str)
    radiobutton_signal = pyqtSignal()
    comboBox_signal = pyqtSignal(list)  #属性选择框信号

    def __init__(self):
        super(ReadThread,self).__init__()

    def run(self) -> None:
        global fileName,selectedFliter,data,data_orignal,databaseUserInformation,sql
        #print('线程开始run了')
        if fileName!='':
            try:
                if '.xlsx' in selectedFliter:
                    data = pd.read_excel(fileName)
                if '.csv' in selectedFliter:
                    data = pd.read_csv(fileName, sep=',')  # sep=','说明分隔符为,header=None 表示没有头部
                if '.db' in selectedFliter:
                    self.con = sqlite3.connect(fileName)  # 数据库连接
                    data = pd.read_sql(sql, self.con)
                data_orignal = data.copy()
                self.sleep(2)  # 即使不需要睡眠也需要添加sleep(0)，目的是让cpu让步
                self.showdata_signal.emit()
                self.radiobutton_signal.emit()
                self.comboBox_signal.emit(list(data.columns))  # 将数据的属性值已列表的形式传送过去
            except Exception as e:
                self.sendException_signal.emit(str(e))
        else:
            self.sleep(0)



class SaveThread(QThread):
    global fileNameSave,selectedfliterSave,data,table_name

    sendSaveException_signal = pyqtSignal(str)

    def __init__(self):
        super(SaveThread, self).__init__()

    def run(self) -> None:
        global fileNameSave,selectedfliterSave,data,fileName,table_name,data_orignal
        if fileNameSave!='':
            try:
                if '.xlsx' in selectedFliter:
                    data = pd.read_excel(fileName)
                if '.csv' in selectedFliter:
                    data = pd.read_csv(fileName, sep=',')  # sep=','说明分隔符为,header=None 表示没有头部
                if '.db' in selectedFliter:
                    self.con = sqlite3.connect(fileName)  # 数据库连接
                    data = pd.read_sql(sql, self.con)
                data_orignal = data.copy()
                self.sleep(2)  # 即使不需要睡眠也需要添加sleep(0)，目的是让cpu让步
                self.showdata_signal.emit()
                self.radiobutton_signal.emit()
                self.comboBox_signal.emit(list(data.columns))  # 将数据的属性值已列表的形式传送过去
            except Exception as e:
                self.sendException_signal.emit(str(e))
        else:
            self.sleep(0)



class StandardDataThread(QThread):
    global data,standard,standard_data

    standardException_signal = pyqtSignal()

    def __init__(self):
        super(StandardDataThread, self).__init__()

    def run(self) -> None:
        global data,standard,standard_data
        standard_data = data.copy()
        if standard_data.empty:
            self.sleep(0)     #即使没有操作也需要在线程中写上sleep(0)，目的是让CPU让步
        else:
            try:
                standard_data = pd.get_dummies(standard_data, sparse=True)  # 进行独热编码
                if standard == 'Minmax':
                    standard_data = (standard_data - standard_data.min()) / (
                                standard_data.max() - standard_data.min())  # 最大最小化
                    print(standard_data)
                if standard == 'xiaoshudingbiao':
                    standard_data = standard_data / (10 ** (np.ceil(np.log10(standard_data.abs().max()))))  # 小数定标标准化
                    print(standard_data)
                if standard == 'Zscore':
                    standard_data = (standard_data - standard_data.mean()) / standard_data.std()  # 标准差标准化
                    print(standard_data)
                self.sleep(2)
            except Exception as e:
                self.standardException_signal.emit(str(e))


class pyechartsThread(QThread):
    global pyechartsdata
    show_pyecharts_signal = pyqtSignal()

    def __init__(self):
        super(pyechartsThread, self).__init__()

    def run(self) -> None:
        c = (
            Bar(
                init_opts=opts.InitOpts(
                    width='330px', height='200px'
                )
            )
                .add_xaxis(list(pyechartsdata['Label']))
                .add_yaxis("属性A", list(pyechartsdata['Count']))

                .set_global_opts(title_opts=opts.TitleOpts(title="Bar-基本示例", subtitle="我是副标题"),
                                 datazoom_opts=opts.DataZoomOpts(range_start=0))

        )
        c.render()
        #self.show_pyecharts_signal.emit()
        self.sleep(2)




'''--------------------------数据库登录界面---------------------------'''
class DataBaseWindow(QtWidgets.QWidget,Ui_Form):
    def __init__(self):
        super(DataBaseWindow, self).__init__()
        self.setupUi(self)
        self.lineEdit_Host.setClearButtonEnabled(True)  #设置清除内容功能
        self.lineEdit_User.setClearButtonEnabled(True)
        self.lineEdit_Password.setClearButtonEnabled(True)
        self.lineEdit_Database.setClearButtonEnabled(True)
        self.setWindowTitle('数据库登录')
        self.setWindowIcon(QtGui.QIcon('Picture/数据库登录界面图标.png'))

    def Warning_QMessageBox(self, content):
        warning = QMessageBox.warning(
            self, ("警告"), content,
            QMessageBox.StandardButtons(QMessageBox.Retry)
        )

    def Information_QMessageBox(self, content):
        information = QMessageBox.information(
            self, '提示', content,
            QMessageBox.StandardButtons(QMessageBox.Ok)
        )





'''-------------------------SQL输入界面---------------------------------'''
class SQLWindow(QtWidgets.QWidget,Ui_SQL):
    def __init__(self):
        super(SQLWindow,self).__init__()
        self.setupUi(self)
        self.setWindowTitle('SQL')
        self.setWindowIcon(QtGui.QIcon('Picture/SQL图标.png'))

    def Warning_QMessageBox(self,content):
        warning = QMessageBox.warning(
            self,("警告"),content,
            QMessageBox.StandardButtons(QMessageBox.Retry)
        )

    def Information_QMessageBox(self,content):
        information = QMessageBox.information(
            self,'提示',content,
            QMessageBox.StandardButtons(QMessageBox.Ok)
        )



if __name__ == '__main__':
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)#保证QT designer设计出来的windows视图跟运行结果视图一样
    app = QtWidgets.QApplication(sys.argv)
    myshow = MainWindows()
    myshow.show()
    sys.exit(app.exec_())

