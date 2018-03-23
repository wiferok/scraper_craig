from PyQt5 import QtCore, QtGui, QtWidgets
from scrapy.utils.project import get_project_settings
import logging




custom_setts = { 'ROOT_LINK': '',
                    'USE_PROXY': True,
                    'STORE_IMAGES': False,
                    'LOG_LEVEL': 4,  # INFO LEVEL
                    }



class XStream(QtCore.QObject):
    _stdout = None
    _stderr = None
    messageWritten = QtCore.pyqtSignal(str)
    def flush( self ):
        pass
    def fileno( self ):
        return -1
    def write( self, msg ):
        if ( not self.signalsBlocked() ):
            self.messageWritten.emit(msg)
    @staticmethod
    def stdout():
        if ( not XStream._stdout ):
            XStream._stdout = XStream()
            sys.stdout = XStream._stdout
        return XStream._stdout
    @staticmethod
    def stderr():
        if ( not XStream._stderr ):
            XStream._stderr = XStream()
            sys.stderr = XStream._stderr
        return XStream._stderr

class QtHandler(logging.Handler):
    def __init__(self, settings):
        logging.Handler.__init__(self)
        formatter = logging.Formatter(
            fmt=settings.get('LOG_FORMAT'),
            datefmt=settings.get('LOG_DATEFORMAT')
        )
        self.setFormatter(formatter)
        self.setLevel(settings.get('LOG_LEVEL'))
        if settings.getbool('LOG_SHORT_NAMES'):
            self.addFilter(TopLevelFormatter(['scrapy']))
    def emit(self, record):
        record = self.format(record)
        if record: XStream.stdout().write('%s\n'%record)
        # originally: XStream.stdout().write("{}\n".format(record))



# logger = logging.getLogger()
# handler = QtHandler()
# logger.addHandler(handler)
# logger.setLevel(logging.DEBUG)


# class TextBrowserHandler(get_scrapy_root_handler()):
#
#     def __init__(self, textBrowserObj, level):
#         super(TextBrowserHandler, self).__init__(level = level)
#         self.textBrowser = textBrowserObj
#
#     def emit(self, record):
#         msg = self.format(record)
#         self.textBrowser.insertPlainText(msg + '\n')


class Ui_ParserWindow(object):

    def __init__(self):
        self.logger = logging.getLogger()
        self.handler = QtHandler(get_project_settings())
        self.logger.addHandler(self.handler)
        self.logger.setLevel(0)
        pass

    def setupUi(self, ParserWindow):
        ParserWindow.setObjectName("ParserWindow")
        ParserWindow.resize(378, 342)
        self.centralwidget = QtWidgets.QWidget(ParserWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.formLayout = QtWidgets.QFormLayout(self.centralwidget)
        self.formLayout.setObjectName("formLayout")
        self.checkDbgMode = QtWidgets.QCheckBox(self.centralwidget)
        self.checkDbgMode.setObjectName("checkDbgMode")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.checkDbgMode)
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setObjectName("label")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label)
        self.textLog = QtWidgets.QTextBrowser(self.centralwidget)
        self.textLog.setObjectName("textLog")
        self.textLog.setReadOnly(True)
        XStream.stdout().messageWritten.connect(self.textLog.append)
        XStream.stderr().messageWritten.connect(self.textLog.append)
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.SpanningRole, self.textLog)
        self.lineUrl = QtWidgets.QLineEdit(self.centralwidget)
        self.lineUrl.setObjectName("lineUrl")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.SpanningRole, self.lineUrl)
        self.startBtn = QtWidgets.QPushButton(self.centralwidget)
        self.startBtn.setObjectName("startBtn")
        self.startBtn.clicked.connect(self.startButton)
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.SpanningRole, self.startBtn)
        self.stopBtn = QtWidgets.QPushButton(self.centralwidget)
        self.stopBtn.setObjectName("stopBtn")
        self.stopBtn.clicked.connect(self.stopButton)
        self.formLayout.setWidget(6, QtWidgets.QFormLayout.LabelRole, self.stopBtn)
        self.settsBtn = QtWidgets.QPushButton(self.centralwidget)
        self.settsBtn.setObjectName("settsBtn")
        self.settsBtn.clicked.connect(self.openSettsBtn)
        self.formLayout.setWidget(6, QtWidgets.QFormLayout.FieldRole, self.settsBtn)
        ParserWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(ParserWindow)
        self.statusbar.setObjectName("statusbar")
        ParserWindow.setStatusBar(self.statusbar)

        self.retranslateUi(ParserWindow)
        QtCore.QMetaObject.connectSlotsByName(ParserWindow)


    def retranslateUi(self, ParserWindow):
        _translate = QtCore.QCoreApplication.translate
        ParserWindow.setWindowTitle(_translate("ParserWindow", "MainWindow"))
        self.checkDbgMode.setText(_translate("ParserWindow", "debug MODE"))
        self.label.setText(_translate("ParserWindow", "Log output:"))
        self.lineUrl.setText(_translate("ParserWindow", "https://boston.craigslist.org/search/hhh"))
        self.startBtn.setText(_translate("ParserWindow", "start"))
        self.stopBtn.setText(_translate("ParserWindow", "stop"))
        self.settsBtn.setText(_translate("ParserWindow", "settings"))

    def stopButton(self):
        print('STOP SIGNAL')
        self.crawl_process.stop()
    def startButton(self):
        custom_setts['ROOT_LINK']= self.lineUrl.text()
        custom_setts['LOG_LEVEL']= logging.DEBUG if \
            self.checkDbgMode.checkState() else logging.INFO
        setts = get_project_settings()
        setts.update(custom_setts)
        self.handler.setLevel(setts['LOG_LEVEL'])
        self.crawl_process = CrawlerRunner(setts)
        self.crawl_process.crawl(CraigSpider(setts))
        d = self.crawl_process.join()
        reactor.run()






    def openSettsBtn(self):
        """open settings"""
        dialog = QtWidgets.QDialog()
        dialog.ui = Ui_Dialog()
        dialog.ui.setupUi(dialog)
        dialog.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        dialog.exec_()

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(194, 129)
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.checkProxies = QtWidgets.QCheckBox(Dialog)
        self.checkProxies.setObjectName("checkProxies")
        self.verticalLayout.addWidget(self.checkProxies, 0, QtCore.Qt.AlignLeft)
        self.checkImages = QtWidgets.QCheckBox(Dialog)
        self.checkImages.setObjectName("checkImages")
        self.verticalLayout.addWidget(self.checkImages, 0, QtCore.Qt.AlignLeft)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(self.save_setts)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.checkProxies.setText(_translate("Dialog", "use proxies"))
        self.checkImages.setText(_translate("Dialog", "save images"))

    def save_setts(self):
        def _set_middlewares():
            #complicated but there is no another way to declare
            if self.checkProxies.checkState():
                custom_setts.update({
                    'DOWNLOADER_MIDDLEWARES':{'scraper_craig.middlewares.ProxyGrabberCheckerMiddleware':101}
                                    })
            else:
                custom_setts.update({
                    'DOWNLOADER_MIDDLEWARES':{'scraper_craig.middlewares.ProxyGrabberCheckerMiddleware':None}
                                    })
            if self.checkImages.checkState():
                custom_setts.update({'ITEM_PIPELINES':{'scraper_craig.pipelines.ImageProcessor':1}
                                     })
            else:
                custom_setts.update({'ITEM_PIPELINES': {'scraper_craig.pipelines.ImageProcessor': None}
                                     })
            #TODO create an shortcut in settings
        _set_middlewares()
class MyApp(QtWidgets.QMainWindow, Ui_ParserWindow):

    def __init__(self):
        super(self.__class__, self).__init()
        self.setupUI(self)





if  __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    import qt5reactor
    qt5reactor.install()
    from scrapy.crawler import CrawlerRunner
    from scraper_craig.spiders.craig_spider import CraigSpider
    from scrapy.utils.log import *
    from twisted.internet import reactor

    window = QtWidgets.QMainWindow()
    ui = Ui_ParserWindow()
    ui.setupUi(window)
    window.show()
    sys.exit(app.exec_())
