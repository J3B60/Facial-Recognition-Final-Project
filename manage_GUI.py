from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import uic
import sys
import time
from datetime import datetime
import webbrowser
import os

#Enrol Imports
from PIL import Image
import cv2
import numpy as np

from sqlFunctions import *
from pgFunctions import *
from guiFunctions import *
from fiFunctions import *

AccessLevelRequirement = 4

class Window(QMainWindow):

    def __init__(self):
        global AccessLevelRequirement
        super().__init__()
        uic.loadUi('rsc/gui/manageGUI.ui', self)

        self.threadpool = QThreadPool()

        self.MenuBarSetup()
        self.Setup()
        if StartPOSTGREsqlServer():#Need to start server before checking UserCredentials
            self.logToTextBrowser("Postgre Server RUNNING")
        else:
            self.logToTextBrowser("Postgre Server FAILED")
            print("startPOSTGRESQLserver.bat file missing?")
            sys.exit()#Early Program Termination
        
        loginBox = loginDialog()
        loginBox.setModal(True)
        loginBox.exec_()
        if loginBox.getAccessLevel() < AccessLevelRequirement:
            print("Login FAILED")
            self.__del__()#Early Program Termination
        self.logToTextBrowser("Postgre Connection SUCCESSFUL")
        self.logToTextBrowser("Login SUCCESSFUL")
        
        self.show()

    def __del__(self):
        StopPOSTGREsqlServer()
        sys.exit()

    def Setup(self):
        self.textBrowser = self.findChild(QTextBrowser, "textBrowser")

#-----------------------------------------------------FILE-----------------------------------------------------

    def OpenSQLfile(self):
        options = QFileDialog.Options()
        FileName, _ = QFileDialog.getOpenFileName(self, "Open SQL File", "", "All Files (*);;SQL Files (*.sql)", options=options)
        if FileName != '':
            f = open(FileName, "r")
            SQLstring = f.read()
            f.close()
            if EXECUTEsqlFile(SQLstring):
                self.logToTextBrowser("Execute SQL statement SUCCESSFUL: " + SQLstring)
            else:
                self.logToTextBrowser("Execute SQL statement FAILED")

    def SaveAs(self):
        options = QFileDialog.Options()
        FileName, _ = QFileDialog.getSaveFileName(self, "Save As...", "", "All Files (*);;Text Files (*.txt)", options=options)
        if FileName != '':
            f = open(FileName, "w+")
            f.write(self.textBrowser.toPlainText())
            f.close()
              
    def backupFaceImages(self):
        buttonReply = QMessageBox.question(self, 'Face Images Backup', "Warning, the program will lockup until backup is complete.\nWould you like to continue?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if buttonReply == QMessageBox.Yes:
            self.logToTextBrowser("Backup STARTED. Please wait...")
            StartFile("backup-FaceImages.bat")
            self.logToTextBrowser("Backup FINISHED")
            return#Stop running function
        self.logToTextBrowser("Backup FAILED or CANCELLED")

    def Export(self):
        ListOfTables = SHOWtableList()#Already in perfect format just returns since [0] is used as explained in the sqlFunctions file
        selectedTable, okPressed = QInputDialog.getItem(self, "Select Table","Table:", ListOfTables, 0, False)
        if okPressed and selectedTable:
            options = QFileDialog.Options()
            FileName, _ = QFileDialog.getSaveFileName(self, "Save To...", "", "All Files (*);;CSV Files (*.csv)", options=options)
            if FileName != '':
                COPYtable(selectedTable, FileName)
                self.logToTextBrowser("Export FINISHED")
                return#Stop running function
        self.logToTextBrowser("Export FAILED or CANCELLED")

#-----------------------------------------------------EDIT_DB-----------------------------------------------------
    
    def show_INSERT_inputBox(self):
        ListOfTables = SHOWtableList()#Already in perfect format just returns since [0] is used as explained in the sqlFunctions file
        selectedTable, okPressed = QInputDialog.getItem(self, "Select Table","Table:", ListOfTables, 0, False)
        if okPressed and selectedTable:
            colNames = SHOWcolumnNames(selectedTable)
            boxText = "("
            for name in colNames:
                boxText = boxText + name + ","
            boxText = boxText + ")"
            text, okPressed = QInputDialog.getText(self, "INSERT Data", boxText + "\nTable Values:", QLineEdit.Normal, "")
            if okPressed and text != '':
                self.logToTextBrowser(selectedTable + " - INSERT: " + text)
                if INSERTentry(selectedTable, tuple(text.split(','))):
                    self.logToTextBrowser("INSERT SUCCESS!")
                else:
                    self.logToTextBrowser("INSERT FAILED!")
            else:
                self.logToTextBrowser("INSERT CANCELLED!")
        else:
            self.logToTextBrowser("INSERT CANCELLED!")

    def show_DELETESQL_inputBox(self):
        ListOfTables = SHOWtableList()#Already in perfect format just returns since [0] is used as explained in the sqlFunctions file
        selectedTable, okPressed1 = QInputDialog.getItem(self, "Select Table","Table:", ListOfTables, 0, False)
        if okPressed1 and selectedTable:
            #EntryID, confirmPressed = QInputDialog.getInt(self, "DELETE Data","Entry ID:", 1, 1, 99999, 1)
            #if confirmPressed:
            colNames = SHOWcolumnNames(selectedTable)
            boxText = "("
            for name in colNames:
                boxText = boxText + name + ","
            boxText = boxText + ")"
            text, okPressed2 = QInputDialog.getText(self, "DELETE Data", boxText+'\nPlease Note, use "" around column Names\nWHERE condition:', QLineEdit.Normal, "")
            if okPressed2 and text != '':
                self.logToTextBrowser(selectedTable + " - DELETE: " + str(text))
                if DELETEentry(selectedTable, text):
                    self.logToTextBrowser("DELETE SUCCESS!")
                else:
                    self.logToTextBrowser("DELETE FAILED!")
            else:
                self.logToTextBrowser("DELETE CANCELLED!")
        else:
            self.logToTextBrowser("DELETE CANCELLED!")

    def show_UPDATESQL_inputBox(self):
        ListOfTables = SHOWtableList()#Already in perfect format just returns since [0] is used as explained in the sqlFunctions file
        selectedTable, okPressed1 = QInputDialog.getItem(self, "Select Table","Table:", ListOfTables, 0, False)
        if okPressed1 and selectedTable:
            #EntryID, confirmPressed = QInputDialog.getInt(self, "DELETE Data","Entry ID:", 1, 1, 99999, 1)
            #if confirmPressed:
            colNames = SHOWcolumnNames(selectedTable)
            boxText = "("
            for name in colNames:
                boxText = boxText + name + ","
            boxText = boxText + ")"
            textSET, okPressed2 = QInputDialog.getText(self, "UPDATE Data", boxText + 'Please Note, use "" around column Names\nSET statement:', QLineEdit.Normal, "")
            if okPressed2 and textSET != '':
                textCON, okPressed3 = QInputDialog.getText(self, "UPDATE Data", boxText + '\nPlease Note, use "" around column Names\nWHERE condition:', QLineEdit.Normal, "")
                if okPressed3 and textCON != '':
                    self.logToTextBrowser(selectedTable + " - UPDATE: " + str(textSET) + " WHERE: " + str(textCON))
                    if UPDATEentrySimple(selectedTable, textSET, textCON):
                        self.logToTextBrowser("UPDATE SUCCESS!")
                    else:
                        self.logToTextBrowser("UPDATE FAILED!")
            else:
                self.logToTextBrowser("UPDATE CANCELLED!")
        else:
            self.logToTextBrowser("UPDATE CANCELLED!")

#-----------------------------------------------------EDIT_FI-----------------------------------------------------

    def show_Add_inputBox(self):
        numImgs, confirmPressed = QInputDialog.getInt(self, "Select number of images","Number of images:", 5, 1, 100, 1)
        if confirmPressed:
            EnrolledUserEntries = SHOWtable("userface")
            EnrolledUserList = []
            for entry in EnrolledUserEntries:
                EnrolledUserList.append(str(entry[0])+ ": " + entry[1] + " " + entry[2])
            userID, okPressed = QInputDialog.getItem(self, "Pick a User","User:", EnrolledUserList, 0, False)
            if okPressed and userID:
                cap = cv2.VideoCapture(0)
                boolList = []
                for i in range(numImgs):
                    boolList.append(CapturePhoto(cap.read(), userID))
                if all(boolList):#If all True
                    self.logToTextBrowser("Add " + str(numImgs) + " Images for " + str(userID) + " SUCCESSFUL")
                else:
                    self.logToTextBrowser("Add " + str(numImgs) + " Images for " + str(userID) + " FAILED")
                

    def show_Delete_inputBox(self):
        deleteBox = deleteDialog()
        deleteBox.setModal(True)
        deleteBox.exec_()
        DeleteList = deleteBox.getDeleteList()#Returns array with Image that were deleted
        for item in DeleteList:#For each file deleted
            self.logToTextBrowser("Delete Face Images for: " + str(item) + "SUCCESSFUL")#Print to the text browser

    def show_DeleteUser_inputBox(self):
        ListOfUserIDs = []
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        image_dir = os.path.join(BASE_DIR, "rsc/Face Images")
        for root, dirs, files in os.walk(image_dir):
            ListOfUserIDs = dirs
            break#Just want the top level in Face Folders, don't need to waste time looking down the directory tree
        ListOfUserIDs.append("All Users not in Database")
        UserID, okPressed = QInputDialog.getItem(self, "Select User to Delete","UserID:", ListOfUserIDs, 0, False)
        ListOfUserIDs.remove("All Users not in Database")#Remove for the purposes of checking the Face Images List against the User Face (Postgre DB) List
        if okPressed and UserID:
            if UserID == "All Users not in Database":
                UserListDB = SHOWtable("userface")
                for entry in UserListDB:#There maybe a better way of doing this for loop and .remove
                    ListOfUsers.remove(entry[0])#entry[0] is the UserID
                    #We will be left with ListOfUsers only containing what is NOT in the DB all other found Users have been removed from the list. We will now use this list to delete this list of users.
                for entry in ListOfUsers:
                    if DeleteUser(entry):#If returns True
                        self.logToTextBrowser("Delete ALL Face Images for: " + str(entry) + "SUCCESSFUL")
                    else:
                        self.logToTextBrowser("Delete ALL Face Images for: " + str(entry) + "FAILED")
            else:
                DeleteUser(UserID)
                self.logToTextBrowser("Delete ALL Face Images for: " + str(UserID) + "SUCCESSFUL")

    def show_ImportImages(self):
        buttonReply = QMessageBox.question(self, 'Face Images Import', "Warning, the program will lockup until import and convert is complete.\nWould you like to continue?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if buttonReply == QMessageBox.Yes:
            #---USERID DIALOG---
            ListOfUserIDs = []
            BASE_DIR = os.path.dirname(os.path.abspath(__file__))
            image_dir = os.path.join(BASE_DIR, "rsc/Face Images")
            for root, dirs, files in os.walk(image_dir):
                ListOfUserIDs = dirs
                break#Just want the top level in Face Folders, don't need to waste time looking down the directory tree
            UserID, okPressed = QInputDialog.getItem(self, "Select UserID","UserID:", ListOfUserIDs, 0, False)
            if okPressed and UserID:
                #---FILE DIALOG---
                options = QFileDialog.Options()
                files, _ = QFileDialog.getOpenFileNames(self,"Import Images", "","All Files (*);;PNG (*.png);;JPEG (*.jpg;*.jpeg)", options=options)
                self.logToTextBrowser("Starting Import and convert, the program will be locked. Please wait...")
                if files:
                    for file in files:
                        if StartFile("importImage.bat " + file + " " + UserID):#WARNING, any file with same name at destination will be overwritten (should add warning box when I have time)
                            self.logToTextBrowser("Import " + file + " for UserID: " + UserID + " SUCCESSFUL")
                        else:
                            self.logToTextBrowser("Import " + file + " for UserID: " + UserID + " FAILED")

#-----------------------------------------------------VIEW-----------------------------------------------------

    def showDBtable(self):
        OUTstr = ""
        ListOfTables = SHOWtableList()#Already in perfect format just returns since [0] is used as explained in the sqlFunctions file
        selectedTable, okPressed = QInputDialog.getItem(self, "Select Table to View","Table:", ListOfTables, 0, False)
        if okPressed and selectedTable:
            ListOfEntries = SHOWtable(selectedTable)
            OUTstr = OUTstr + "View: " + selectedTable
            ListOfColumns = SHOWcolumnNames(selectedTable)
            OUTstr = OUTstr + "\n"
            for ColName in ListOfColumns:
                OUTstr = OUTstr + ColName + ", "
            for entry in ListOfEntries:
                OUTstr = OUTstr + "\n"
                for item in entry:
                    OUTstr = OUTstr + str(item) + ", "
        else:
            OUTstr = "Show Table Cancelled"
        self.logToTextBrowser(OUTstr)

    def showImagesList(self):
        OUTstr = "View: Face Images\n"#Output to TextBrowser
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))#Same as other code
        image_dir = os.path.join(BASE_DIR, "rsc/Face Images")#Same as other code
        for root, dirs, files in os.walk(image_dir):
            for file in files:
                path = os.path.join(root, file)#Root contains the current UserID. we just need to extract it using basename
                OUTstr = OUTstr + str(os.path.basename(os.path.dirname(path))) + "/" + str(file) + "\n"#First lists all dirs in (files are None) then lists all dirs with files
        self.logToTextBrowser(OUTstr)
        
#-----------------------------------------------------RUN--------------------------------------------------------

    def runEnrol(self):#Just copied from enrol_GUI runEnrol()
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
        if F:
            self.progbar.accept()
            self.logToTextBrowser("Enrollment SUCCESSFUL")
        else:
            self.progbar.reject()
            self.logToTextBrowser("Enrollment FAILED")

#-----------------------------------------------------SETTINGS-----------------------------------------------------

    def openConfig(self):
        StartFile("openConfigFiles.bat")
        

#-----------------------------------------------------TXT_BR-----------------------------------------------------
            
    def textBrowserClear(self):
        self.textBrowser.clear()

    def logToTextBrowser(self, logEntry):
        dtn = datetime.now()
        self.textBrowser.append("[" + str(dtn.year) +"-"+ str(dtn.month) +"-"+ str(dtn.day) +" "+ str(dtn.hour) +":"+ str(dtn.minute) +":"+ str(dtn.second) +"] " + logEntry)

#-----------------------------------------------------MENUBAR-----------------------------------------------------

    def MenuBarSetup(self):
        menubar = self.findChild(QMenuBar, "menuBar")#Import

        #-File-
        menuFile = self.findChild(QMenu, "menuFile")#Import
        mF_actionSave_As = self.findChild(QAction, "actionSave_As")#Import
        actionExit = self.findChild(QAction, "actionExit")#Import
        actionBackup = self.findChild(QAction, "actionBackup")#Import
        actionExport = self.findChild(QAction, "actionExport")#Import
        actionExport.triggered.connect(self.Export)
        actionExit.triggered.connect(sys.exit)#ACTION
        mF_actionSave_As.triggered.connect(self.SaveAs)#ACTION
        actionBackup.triggered.connect(self.backupFaceImages)#ACTION
        
        #-File>Run-
        menuRun = self.findChild(QMenu, "menuRun")#Import
        mFR_action_sql_file = self.findChild(QAction, "action_sql_file")#Import
        mFR_action_sql_file.triggered.connect(self.OpenSQLfile)#ACTION
        
        #-Edit-
        menuEdit = self.findChild(QMenu, "menuEdit")#Import
        
        #-Edit>SQL-
        menuSQL_Function = self.findChild(QMenu, "menuSQL_Functions")#Import
        actionINSERT = self.findChild(QAction, "actionINSERT")#Import
        actionDELETE = self.findChild(QAction, "actionDELETE")#Import
        actionUPDATE = self.findChild(QAction, "actionUPDATE")#Import
        actionINSERT.triggered.connect(self.show_INSERT_inputBox)#ACTION
        actionDELETE.triggered.connect(self.show_DELETESQL_inputBox)#ACTION
        actionUPDATE.triggered.connect(self.show_UPDATESQL_inputBox)#ACTION

        #-Edit>Face_Images-
        menuFace_Images = self.findChild(QMenu, "menuFace_Images")#Import
        actionAdd = self.findChild(QAction, "actionAdd")#Import #TAKE PHOTO
        actionDelete = self.findChild(QAction, "actionDelete")#Import
        actionAddImg = self.findChild(QAction, "actionAddImg")#Import #IMPORT IMAGES
        actionDeleteUser = self.findChild(QAction, "actionDelete_User")#Import
        actionAdd.triggered.connect(self.show_Add_inputBox)#ACTION
        actionDelete.triggered.connect(self.show_Delete_inputBox)#ACTION
        actionDeleteUser.triggered.connect(self.show_DeleteUser_inputBox)#ACTION
        actionAddImg.triggered.connect(self.show_ImportImages)#ACTION

        #-View-
        menuView = self.findChild(QMenu, "menuView")#Import
        actionTable = self.findChild(QAction, "actionTable")#Import
        actionImages = self.findChild(QAction, "actionImages")#Import
        actionClear = self.findChild(QAction, "actionClear")#Import
        actionTable.triggered.connect(self.showDBtable)#ACTION
        actionImages.triggered.connect(self.showImagesList)#ACTION
        actionClear.triggered.connect(self.textBrowserClear)#ACTION

        #-Run-
        menuRun_2 = self.findChild(QMenu, "menuRun_2")#Import
        actionRecognition_Train = self.findChild(QAction, "actionRecognition_Train")#Import
        actionRecognition_Train.triggered.connect(self.runEnrol)#ACTION

        #-Settings-
        menuSettings = self.findChild(QMenu, "menuSettings")#Import
        actionConfig = self.findChild(QAction, "actionConfig_Files")#Import
        actionConfig.triggered.connect(self.openConfig)#ACTION
        
        #-Tools-
        menuTools = self.findChild(QMenu, "menuTools")#Import
        actionEnrol_GUI = self.findChild(QAction, "actionEnrol_GUI")#Import
        actionMonitor = self.findChild(QAction, "actionMonitor")#Import
        actionSecurity = self.findChild(QAction, "actionSecurity")#Import
        actionpgAdmin4 = self.findChild(QAction, "actionpgAdmin4")#Import
        actionEnrol_GUI.triggered.connect(lambda: self.open_Tool(1))#ACTION
        actionMonitor.triggered.connect(lambda: self.open_Tool(2))#ACTION
        actionSecurity.triggered.connect(lambda: self.open_Tool(3))#ACTION
        actionpgAdmin4.triggered.connect(lambda: self.open_Tool(4))#ACTION

        #-Help-
        menuHelp = self.findChild(QMenu, "menuHelp")#Import
        mH_actionAbout = self.findChild(QAction, "actionAbout")#Import
        mH_actionAbout_2 = self.findChild(QAction, "actionAbout_2")#Import
        mH_actionAbout.triggered.connect(self.open_WebBrowser_Help)#ACTION
        mH_actionAbout_2.triggered.connect(self.open_WebBrowser_About)#ACTION

    #-----------------------------------------------------TOOLS-----------------------------------------------------

    def open_Tool(self, option):
        buttonReply = QMessageBox.question(self, 'Warning', "Warning:\nThis will close Manage.\nAny unsaved progress will be lost.\n\nContinue?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if buttonReply == QMessageBox.Yes:
            if option == 1:#ENROL
                os.system('enrol_GUI.py')####TODO - THIS SHOULD BE MADE TO WORK WITH StartFile() (but it's fine as is for now)
                sys.exit()
            elif option == 2:#MONITOR
                os.system('monitor_GUI.py')####TODO - THIS SHOULD BE MADE TO WORK WITH StartFile() (but it's fine as is for now)
                sys.exit()   
            elif option == 3:#SECURITY
                os.system('security_GUI.py')####TODO - THIS SHOULD BE MADE TO WORK WITH StartFile() (but it's fine as is for now)
                sys.exit()
            elif option == 4:#PGADMIN4
                StartPgAdmin4()
                sys.exit()
            else:
                print("Error Code: 000001")#Just catch and print to console (Might be a better idea to make a seperate function for making an error log file.)
        else:#Else, do nothing, just close the message box
            pass
    
    #-----------------------------------------------------HELP------------------------------------------------------
    def open_WebBrowser_Help(self):
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))#Gets this python file's path excluding file name
        PATH = os.path.join(BASE_DIR, "rsc/doc/help/Manage.html")
        webbrowser.open(PATH)

    def open_WebBrowser_About(self):
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))#Gets this python file's path excluding file name
        PATH = os.path.join(BASE_DIR, "rsc/doc/about/Manage.txt")
        webbrowser.open(PATH)

#------------------GENERIC FUNCTION THREAD--------------------------------

class WorkerSignals(QObject):
    finished = pyqtSignal()
    result = pyqtSignal(bool)

class Worker(QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()
        self.fn = fn
        self.signals = WorkerSignals()

    @pyqtSlot()
    def run(self):
        if self.fn():
            self.signals.result.emit(False)
        else:
            self.signals.result.emit(False)
        #self.signals.finished.emit()

#--------------------------------------ENROL THREAD---------------------------
class EnrolThreadSignals(QObject):#FROM enrol_GUI exct Copy
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
