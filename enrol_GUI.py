from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import uic
import sys
import time
import numpy as np
import cv2
import webbrowser
import os
from PIL import Image

from fiFunctions import *
from guiFunctions import *
from pgFunctions import *
from sqlFunctions import *

cap = cv2.VideoCapture(0)
#CamFeedpause = False
AccessLevelRequirement = 2
CaptureMode = 1#FROM INI FILE

class Window(QMainWindow):

    def __init__(self):
        global AccessLevelRequirement
        super(Window, self).__init__()
        uic.loadUi('rsc/gui/enrolGUI.ui', self)

        self.threadpool = QThreadPool()

        StartPOSTGREsqlServer()#Need to start server before checking UserCredentials

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

    def Setup(self):
        self.enrolBtn = self.findChild(QPushButton, "enrolBtn")
        self.enrolBtn.clicked.connect(self.EnrolUser)
        self.CameraFeedLbl = self.findChild(QLabel, 'CameraFeedLbl')
        self.FaceStatus = self.findChild(QLabel, 'FaceStatus')

    def MenuBarSetup(self):
        menubar = self.findChild(QMenuBar, "menuBar")#Import
        #--Help--
        menuHelp = self.findChild(QMenu, "menuHelp")#Import
        mH_actionHelp = self.findChild(QAction, "actionHelp")#Import
        mH_actionAbout = self.findChild(QAction, "actionAbout")#Import
        mH_actionHelp.triggered.connect(self.open_WebBrowser_Help)#ACTION
        mH_actionAbout.triggered.connect(self.open_WebBrowser_About)#ACTION

    def open_WebBrowser_Help(self):
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))#Gets this python file's path excluding file name
        PATH = os.path.join(BASE_DIR, "rsc/doc/help/Enrol.html")
        webbrowser.open(PATH)

    def open_WebBrowser_About(self):
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))#Gets this python file's path excluding file name
        PATH = os.path.join(BASE_DIR, "rsc/doc/about/Enrol.txt")
        webbrowser.open(PATH)

    def showCameraFeed(self, s,v):
        self.CameraFeedLbl.setPixmap(s)
        self.currentFrame = v#Variable to get the frame, better to use this maybe rather than getting cap.read() collisions
        #Need to come up with a better method for self.currentFrame, it works great but logically not ideal since I'm passing both a Pixmap and the frame which is duplicate data andcould be sorted out better

    def getCameraFeed(self):
        worker = CameraFeedThread()
        
        worker.signals.result.connect(self.showCameraFeed)
        #finished.connect()#Not used

        self.threadpool.start(worker)

    #--When Enrol Button Clicked--
    def EnrolUser(self):
        global cap
        global CaptureMode
        #global CamFeedpause
        #CamFeedpause = True
        if not cap.isOpened():
            QMessageBox.question(self, "Error", "Camera is not connected", QMessageBox.Ok)
            return
        FName, okPressed = QInputDialog.getText(self, "User Name Input", "First Name:", QLineEdit.Normal, "")
        if okPressed and FName != '':
            LName, okPressed = QInputDialog.getText(self, "User Name Input", "Last Name:", QLineEdit.Normal, "")
            if okPressed and LName != '':
                valid = False
                while valid == False:
                    ListOfIDs = []
                    UserFaceList = SHOWtable("userface")
                    for entry in UserFaceList:
                        ListOfIDs.append(int(entry[0]))
                    ListOfIDs.sort()
                    nextValidUserID = ListOfIDs[len(ListOfIDs) -1] + 1
                    selectedUserID, confirmPressed = QInputDialog.getInt(self, "Set UserID","UserID", nextValidUserID, 10000, 99999, 1)
                    if confirmPressed:
                        if selectedUserID not in ListOfIDs:
                            valid = True#Valid UserID selected
                            AddUserID(selectedUserID)#DEBUG should be guarantee True because ID is valid, but turn this into an if statement incase postgre and 'face images' folder don't match
                            for x in range(10):#We want 10 images of the face
                                while CaptureMode == 0:#Capture indefinitly until a face is detected
                                    if CapturePhoto(self.currentFrame, selectedUserID):#With face detect so we will not store images that dont contain face
                                        break
                                while CaptureMode == 1:#Capture indefinitly until a face is detected
                                    if CapturePhotoWfaceDetect(self.currentFrame, selectedUserID):#With face detect so we will not store images that dont contain face
                                        break
                                while CaptureMode == 2:#Capture indefinitly until a face is detected
                                    if CapturePhotoFaceROI(self.currentFrame, selectedUserID):#With face detect so we will not store images that dont contain face
                                        break
                            INSERTentry("userface", (selectedUserID,FName,LName))
                            self.runEnrol()

    def runEnrol(self):
        worker = EnrolThread()

        worker.signals.EnrolProgress.connect(self.updateProgressBar)
        worker.signals.textChange.connect(self.setTextProgressBar)
        worker.signals.finished.connect(self.completedEnrol)
        
        self.threadpool.start(worker)

        self.progbar = progbarDialog()
        self.progbar.setModal(True)
        self.progbar.exec_()

    def updateProgressBar(self, value):
        #print(value)#DEBUG, TEMP until progbar finished
        self.progbar.setProgBarValue(value)

    def setTextProgressBar(self, text):
        #print(text)#DEBUG, TEMP until progbar finished
        self.progbar.setProgBarLabel(text)

    def completedEnrol(self, F):
        #global CamFeedpause
        #CamFeedpause = False
        if F:
            self.progbar.accept()
            QMessageBox.question(self, "Finised", "Enrollment Finished", QMessageBox.Ok)
        else:
            self.progbar.reject()
            QMessageBox.question(self, "Error", "Enrollment Error", QMessageBox.Ok)

class CameraFeedThreadSignals(QObject):
    finished = pyqtSignal()
    result = pyqtSignal(object,object)

class CameraFeedThread(QRunnable):
    def __init__(self):
        super(CameraFeedThread, self).__init__()
        self.signals = CameraFeedThreadSignals()

    @pyqtSlot()
    def run(self):
        global cap
        #global CamFeedpause
        while cap.isOpened(): #and CamFeedpause == False:
            img = cap.read()[1]
            self.signals.result.emit(CameraToGUI(img),img)#NEW,just passing img too just to try out if I can capture it

class EnrolThreadSignals(QObject):
    EnrolProgress = pyqtSignal(int)
    finished = pyqtSignal(bool)
    textChange = pyqtSignal(str)

class EnrolThread(QRunnable):
    def __init__(self):
        super(EnrolThread, self).__init__()
        self.signals = EnrolThreadSignals()
        self.face_cascade = cv2.CascadeClassifier('rsc/haar/haarcascade_frontalface_default.xml')#Run once, this runs when Thread Init

    #def __del__(self):
    #    pass

    @pyqtSlot()  
    def run(self):
        #NOTE Problem with just using the face_recog_trainer function from fsysFunction is that there is no way to get progress feedback since need to integrate PyQt5 signal within the code.
        #So this code below is just copied from the face_recog_train function with pyqtSignal added in.
        currentImgNumber = 0
        NumOfFiles = 0
        ####FROM FUNC
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        image_dir = os.path.join(BASE_DIR, "rsc/Face Images")
        
        for root, dirs, files in os.walk(image_dir):
            for file in files:
                if file.endswith("png") or file.endswith("jpg") or file.endswith("JPG") or file.endswith("PNG"):
                    NumOfFiles = NumOfFiles + 1
                    
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        
        y_labels = []
        x_train = []
        
        for root, dirs, files in os.walk(image_dir):
            for file in files:
                if file.endswith("png") or file.endswith("jpg") or file.endswith("JPG") or file.endswith("PNG"):
                    self.signals.EnrolProgress.emit(int(currentImgNumber*100/NumOfFiles))#PYQTSIGNAL
                    currentImgNumber = currentImgNumber + 1
                    path = os.path.join(root, file)
                    label = os.path.basename(os.path.dirname(path))
                    #print(label, path)#DEBUG
                    
                    pil_image = Image.open(path).convert("L")
                    image_array = np.array(pil_image, "uint8")
                    #print(image_array)#DEBUG
                    
                    #NOTE NEED TO MESS AROUND WITH THE detectMultiScale() Parameters to get best results (1.3, 5) is the old magic combination, another good one is (1.5, 5). Using default results in more of the lower quality images being used (hence bigger trainner.yml files). Need to actually test what is best.
                    faces = self.face_cascade.detectMultiScale(image_array)#, 1.3,5)#So unlike face_detection_bool, this has no cv2.cvtColor so this is a remake of the function otherwise they work the same
                    for (x,y,w,h) in faces:
                        roi = image_array[y:y+h, x:x+w]
                        x_train.append(roi)
                        y_labels.append(int(label))
        
        if not x_train == []:
            self.signals.textChange.emit("Now Training. Please wait a few minutes...")
            recognizer.train(x_train, np.array(y_labels))
            recognizer.save("trainner.yml")
            self.signals.finished.emit(True)#REPLACE RETURN STATEMENT
        else:
            self.signals.finished.emit(False)#REPLACE RETURN STATEMENT
       

app = QApplication(sys.argv)
GUI = Window()
sys.exit(app.exec_())
