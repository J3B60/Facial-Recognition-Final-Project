from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import uic
import sys
import time
from datetime import datetime
import cv2
import webbrowser
import os

from sqlFunctions import SHOWtable
from guiFunctions import CameraToGUI, loginDialog
from pgFunctions import *

cap = cv2.VideoCapture(0)
AccessLevelRequirement = 3

class Window(QMainWindow):

    def __init__(self):
        global AccessLevelRequirement
        super(Window, self).__init__()
        uic.loadUi('rsc/gui/monitorGUI.ui', self)

        self.threadpool = QThreadPool()

        StartPOSTGREsqlServer()

        loginBox = loginDialog()
        loginBox.setModal(True)
        loginBox.exec_()
        if loginBox.getAccessLevel() < AccessLevelRequirement:
            print("Login FAILED")
            self.__del__()#Early Program Termination

        self.MenuBarSetup()
        self.Setup()
        self.getCameraFeed()
        self.show()

    def __del__(self):
        global cap
        cap.release()
        StopPOSTGREsqlServer()
        os._exit(1)

    def showCameraFeed(self, s):
        self.mainCFeed.setPixmap(s)

    def getCameraFeed(self):
        worker = CameraFeedThread()
        
        worker.signals.result.connect(self.showCameraFeed)
        #worker.signals.finished.connect(self.thread_complete)#NOT NEEDED
        self.threadpool.start(worker)

    def show_SaveAs_inputBox(self):
        options = QFileDialog.Options()
        FileName, _ = QFileDialog.getSaveFileName(self, "Save As...", "", "Text Files (*.txt);;All Files (*)", options=options)
        if FileName != '':
            f = open(FileName, "w+")
            f.write(self.mainCLog.toPlainText())

    def show_Open_inputBox(self):
        global cap
        #IM KEEPING THE OLD CODE JUST INCASE THE NEW ONE CAUSES PROBLEMS BUT FROM WHAT IVE SEEN IN TESTS IT SHOULD BE FINE
        #CameraEntries = SHOWtable("camera")#OLD
        #CameraList = []#OLD
        #for entry in CameraEntries:#OLD
            #CameraList.append(entry[1])#OLD
        CameraEntries = SHOWtable("camera")
        RoomEntries = SHOWtable("room")
        CameraList = []
        for CEntry in CameraEntries:
            for REntry in RoomEntries:
                if REntry[0] == CEntry[0]:
                    CameraList.append(str(REntry[2])+": "+ str (CEntry[1]))
        camera, okPressed = QInputDialog.getItem(self, "Open","Camera:", CameraList, 0, False)
        if okPressed and camera:
            #NEED TO CHECK IF CAMERA IS AVAILABLE BEFORE FORCING ON THIS CONNECTION. NEED TO ADD OPTION FOR LOCAL CAMERA, NEED TO PREVENT USER FROM PICKING THE SAME CAMERA, COULD ADD LABEL TO SHOW WHICH CAMERA IS CURRENTLY ON THE CAMERA FEED
            cap = cv2.VideoCapture(CameraEntries[CameraList.index(camera)][2])
            self.mainCLog.clear()
            #print(CameraEntries[CameraList.index(camera)][1])#DEBUG
            #print(CameraEntries[CameraList.index(camera)][4])#DEBUG
            self.mainCLog.append("Camera: "+str(CameraEntries[CameraList.index(camera)][1]) + " LOG\n" + str(CameraEntries[CameraList.index(camera)][4]))
            
    def Setup(self):
        self.mainCFeed = self.findChild(QLabel, "mainCFeed")#Import
        self.mainCLog = self.findChild(QTextBrowser, "mainCLog")#Import

    def MenuBarSetup(self):
        menubar = self.findChild(QMenuBar, "menuBar")#Import

        #--File--
        menuFile = self.findChild(QMenu, "menuFile")#Import
        mF_actionSaveAs = self.findChild(QAction, "actionSaveAs")#Import
        mF_actionOpen = self.findChild(QAction, "actionOpen")#Import
        mF_actionExit = self.findChild(QAction, "actionExit")#Import
        mF_actionSaveAs.triggered.connect(self.show_SaveAs_inputBox)#ACTION
        mF_actionOpen.triggered.connect(self.show_Open_inputBox)#ACTION
        mF_actionExit.triggered.connect(sys.exit)#ACTION

        #--Help--
        menuHelp = self.findChild(QMenu, "menuHelp")#Import
        mH_actionHelp = self.findChild(QAction, "actionHelp")#Import
        mH_actionAbout = self.findChild(QAction, "actionAbout")#Import
        mH_actionHelp.triggered.connect(self.open_WebBrowser_Help)#ACTION
        mH_actionAbout.triggered.connect(self.open_WebBrowser_About)#ACTION

    def open_WebBrowser_Help(self):
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))#Gets this python file's path excluding file name
        PATH = os.path.join(BASE_DIR, "rsc/doc/help/Monitor.html")
        webbrowser.open(PATH)

    def open_WebBrowser_About(self):
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))#Gets this python file's path excluding file name
        PATH = os.path.join(BASE_DIR, "rsc/doc/about/Monitor.txt")
        webbrowser.open(PATH)

class CameraFeedThreadSignals(QObject):
    finished = pyqtSignal()
    result = pyqtSignal(object)

class CameraFeedThread(QRunnable):
    def __init__(self):
        super(CameraFeedThread, self).__init__()
        self.signals = CameraFeedThreadSignals()
    
    @pyqtSlot()
    def run(self):
        global cap
        #DEBUGcount =0
        while True:
            #DEBUGcount = DEBUGcount +1
            #print(str(cap.isOpened()) +" "+ str(DEBUGcount))
            if cap.isOpened():
                img = cap.read()[1]
                self.signals.result.emit(CameraToGUI(img))
            #else:
                #self.terminate()

app = QApplication(sys.argv)
GUI = Window()
sys.exit(app.exec_())
