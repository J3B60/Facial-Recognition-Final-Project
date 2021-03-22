from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import uic

import psycopg2

import cv2

from sqlFunctions import CheckUserCredentials

import subprocess
import os
import platform

from fiFunctions import GetImgList, DeleteUserImage

#NOTES of changes compared to original .py function Files.
#loginDialog has been fixed to use database.ini, using iniFileParser

def CameraToGUI(img):
    CameraFeedArray = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    height, width= CameraFeedArray.shape[0:2]#Ignore channels from .shape
    bytesPerLine = 3 * width
    CameraFeedImg = QImage(CameraFeedArray, width, height, bytesPerLine, QImage.Format_RGB888)
    CameraFeedPixmap = QPixmap.fromImage(CameraFeedImg)
    return CameraFeedPixmap

class loginDialog(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi('rsc/gui/loginDialog.ui', self)
        self.result = 0
        self.Setup()

    def Setup(self):
        self.userNameField = self.findChild(QLineEdit, "userNameField")#Import
        self.passwordField = self.findChild(QLineEdit, "passwordField")#Import
        buttonBox = self.findChild(QDialogButtonBox, "buttonBox")#Import
        buttonBox.accepted.connect(self.acceptFunc)#ACTION
        buttonBox.rejected.connect(self.rejectFunc)#ACTION

    def getAccessLevel(self):
        return self.result

    def acceptFunc(self):
        #print("We are here in LoginDialog.acceptFunc")#DEBUG
        self.result = CheckUserCredentials(self.userNameField.text(),self.passwordField.text())
        self.accept()
        
    def rejectFunc(self):
        self.reject()

def StartFile(file):
    if platform.system() == 'Windows':
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))#Gets this python file's path excluding file name
        #NOTE __file__ is this python file's path including the file name
        subprocess.call(file, cwd=BASE_DIR, shell=True)
        return True
    else:
        return False#Currently can only start POSTGRESQL windows from windows. Need different platform POSTGRE for other OS

class deleteDialog(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi('rsc/gui/deleteFIDialog.ui', self)
        self.DeleteList = []
        self.Setup()
        self.show()

    def Setup(self):
        self.label = self.findChild(QLabel, "label")#Import
        self.listWidget = self.findChild(QListWidget, "listWidget")#Import
        self.buttonBox = self.findChild(QDialogButtonBox, "buttonBox")#Import
        self.buttonBox.accepted.connect(self.acceptFunc)#ACTION#Left over from Ok
        self.buttonBox.rejected.connect(self.rejectFunc)#ACTION#Left Over from cancel
        self.listWidget.addItems(GetImgList())#Note addItems() not addItem()
        self.listWidget.currentItemChanged.connect(self.updateView)#ACTION
        #####self.buttonBox.setStandardButtons(QDialogButtonBox.Discard|QDialogButtonBox.Close)
        self.buttonBox.button(QDialogButtonBox.Discard).clicked.connect(self.delFunc)#ACTION#Discard Button
        #Close button will just close without having to define in the python code.
        #print(self.db)#DEBUG

    def updateView(self):
        if not self.listWidget.currentItem()== None :
            currentImg = QPixmap("rsc/Face Images/" + self.listWidget.currentItem().text()) #Add path from item
            self.label.setPixmap(currentImg)
            self.show()
    
    def delFunc(self):#Don't close
        UserID, imgFile =self.listWidget.currentItem().text().split("/")#parse file path to get UserID and Img NUmber
        imgFileNumber, ext = imgFile.split(".")#Ignore file extension #NOTE Can only delete PNG files
        DeleteUserImage(UserID, imgFileNumber)#str(string) is same as just string so the fact that this is passing a sting and not integers is fine.
        self.DeleteList.append(self.listWidget.currentItem().text())
        #print(UserID, imgFileNumber)#DEBUG
        self.listWidget.clear()#Clear list
        #print("We Here")#DEBUG
        self.listWidget.addItems(GetImgList())#Note addItems() not addItem() #Re-add everything
        #print("Hows it going")#DEBUG
        #self.show()#Show#Update Dialog

    def getDeleteList(self):
        return self.DeleteList
    
    def acceptFunc(self):
        #print("Does this Work")
        pass#TEMP
    
    def rejectFunc(self):
        self.reject()

class progbarDialog(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi('rsc/gui/progbarDialog.ui', self)
        self.Setup()
        #self.show()

    def Setup(self):
        self.label = self.findChild(QLabel, "label")#Import
        self.progressBar = self.findChild(QProgressBar, "progressBar")#Import
        self.buttonBox = self.findChild(QDialogButtonBox, "buttonBox")#Import
        self.buttonBox.rejected.connect(self.rejectFunc)#ACTION

    def setProgBarLabel(self, text):
        self.label.setText(text)
        self.update()

    def setProgBarValue(self, value):
        self.progressBar.setValue(value)
        self.update()
        
    def rejectFunc(self):
        self.reject()

#-test-
#print(iniFileParser("database.ini",'postgresql'))

#print(CheckUserCredentials('n','p'))

#print(StartFile("backup-FaceImages.bat"))
