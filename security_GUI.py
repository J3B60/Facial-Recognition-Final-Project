from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import uic
import sys

import cv2

import time
from datetime import datetime

from pgFunctions import *
from sqlFunctions import *
from guiFunctions import loginDialog
from fsysFunctions import *

AccessLevelRequirement = 1

cap = None

AutoLockSeconds = 15
start_time = 0
SelectedCameraID = 0
SelectedRoomID = 0

class Window(QMainWindow):

    def __init__(self):
        global AccessLevelRequirement
        super(Window, self).__init__()
        uic.loadUi('rsc/gui/securityGUI.ui', self)

        self.threadpool = QThreadPool()

        StartPOSTGREsqlServer()
        
        loginBox = loginDialog()
        loginBox.setModal(True)
        loginBox.exec_()
        if loginBox.getAccessLevel() < AccessLevelRequirement:
            print("Login FAILED")
            self.__del__()#Early Program Termination

        self.Setup()

        self.CameraSelect()

        self.CameraRecognitionSetup()
        
        self.show()

    def __del__(self):
        global cap
        if not cap == None:
            cap.release()
        StopPOSTGREsqlServer()
        os._exit(1)
        

    def Setup(self):
        self.accessImg = self.findChild(QLabel, 'accessImg')
        self.accessInfo = self.findChild(QLabel, 'accessInfo')
        self.LockImg = QPixmap("rsc/gui/icon/lockGUIiconLarge.png")
        self.accessGrantImg = QPixmap("rsc/gui/icon/personIconLarge.png")
        self.centralwidget = self.findChild(QWidget, 'centralwidget')

    def CameraSelect(self):
        global cap
        global SelectedCameraID
        global SelectedRoomID
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
            SelectedRoomID = CameraEntries[CameraList.index(camera)][0]
            SelectedCameraID = CameraEntries[CameraList.index(camera)][3]
        else:
            cap = cv2.VideoCapture(0)#TEMP, should exit, need to add local camera for testing#I'll Leave this as a secret setting
            #sys.exit()

    def CameraRecognitionSetup(self):
        self.worker = CameraFeedThread()
        
        self.worker.signals.result.connect(self.accessDecision)
        self.threadpool.start(self.worker)

    #LabelValSet = []
    #NumOfFrames = 1
    #CollectiveThreshold = 0
    
    def accessDecision(self, label):#label[0]=UserID, label[1]=FaceRecog_Confidence
        global SelectedRoomID
        global SelectedCameraID
        global start_time
        global AutoLockSeconds
        end_time = time.time()
        T = end_time - start_time
        if T > AutoLockSeconds:
            #global LabelValSet
            #global NumOfFrames
            #global CollectiveThreshold
            #if len(LabelValSet) < NumOfFrames:
            #    LabelValSet.append(label)
            #else:
            #    LabelList = [i[0] for i in LabelValSet]
            #    ValList = [j[0] for j in LabelValSet]
            #    if (all(i == LabelList[0] for i in LabelList) and all(j > CollectiveThreshold for j in ValList)):#place holder            
            if (not label == None):
                print("We Are Here")
                if any(i == SelectedRoomID for i in SHOWuserAccess(label[0])):
                    self.accessImg.setPixmap(self.accessGrantImg)
                    self.accessInfo.setText("Access Granted to "+str(label[0]))#LabelList[0]))
                    self.centralwidget.setStyleSheet("background-color: rgb(74, 226, 4)")
                    dtn = datetime.now()
                    APPENDcameraLog("[" + str(dtn.year) +"-"+ str(dtn.month) +"-"+ str(dtn.day) +" "+ str(dtn.hour) +":"+ str(dtn.minute) +":"+ str(dtn.second) +"] ACCESS-GRANTED to UserID ", SelectedCameraID, label[0])
                else:
                    self.accessImg.setPixmap(self.LockImg)
                    self.centralwidget.setStyleSheet("background-color: rgb(218, 24, 24)")
                    self.accessInfo.setText("Access Denied to "+str(label[0]))
                    dtn = datetime.now()
                    APPENDcameraLog("[" + str(dtn.year) +"-"+ str(dtn.month) +"-"+ str(dtn.day) +" "+ str(dtn.hour) +":"+ str(dtn.minute) +":"+ str(dtn.second) +"] ACCESS-GRANTED to UserID ", SelectedCameraID, label[0])
                start_time = time.time()        
            else:
                self.Idle(SelectedRoomID)
            self.update()
            #time.sleep(5)#Sleep for 5 seconds then return to Idle state/Closed Door
                #LabelSet = []

    def Idle(self, roomNum):
        self.accessImg.setPixmap(self.LockImg)
        self.centralwidget.setStyleSheet("background-color: rgb(76, 76, 76)")
        self.accessInfo.setText("Room " + str(roomNum))
        self.update()

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
                self.signals.result.emit(face_recog(img))

app = QApplication(sys.argv)
GUI = Window()
#GUI.accessDecision(False)#DEBUG
#GUI.Idle(1)#Return to Original#DEBUG
sys.exit(app.exec_())
