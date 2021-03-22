import os
import os.path
import time
import cv2
import shutil

from fsysFunctions import *

def AddUserID(UserID):
    if(IsUserFaceFolder(UserID)):
        return False
    else:
        os.mkdir("rsc/Face Images/" + str(UserID))
        return True

def CapturePhoto(frame, UserID):#Force ccapture photo
    if frame is None:#Not sure how much of an effect this will have :(
        return False
    else:
        cv2.imwrite(GetUserImagePath(UserID, NextUserImage(UserID)), frame)    #Need to fix to have NextUserImage
        return True

def CapturePhotoWfaceDetect(frame, UserID):#Ensures save good photos (bad photos aren't used in recognition training anyway so this saves HardDrive space)
    if frame is None:
        return False
    else:
        if face_detectBool(frame):
            cv2.imwrite(GetUserImagePath(UserID, NextUserImage(UserID)), frame)    #Need to fix to have NextUserImage
            return True
        else:
            return False

def CapturePhotoFaceROI(frame, UserID):#Ensures save good photos (bad photos aren't used in recognition training anyway so this saves HardDrive space)
    if frame is None:
        return False
    else:
        IMG = face_detectROI(frame)
        if IMG is None:
            return False
        else:
            cv2.imwrite(GetUserImagePath(UserID, NextUserImage(UserID)), IMG)    #Need to fix to have NextUserImage
            return True

def DeleteUserImage(ID, imgNum):#ID CAN BE INT OR STR, IT WILL BE CONVERTED, SAFE TO USE
    if (IsUserImage(ID, imgNum)):
        os.remove(GetUserImagePath(ID,imgNum))
        return True
    else:
        return False

def DeleteUser(ID):#ID CAN BE INT OR STR, IT WILL BE CONVERTED WHERE REQUIRED
    if IsUserFaceFolder(ID):
        shutil.rmtree("rsc/Face Images/"+str(ID),ignore_errors=True)
        return True
    else:
        return False

def GetImgList():
    ListOfFiles = []
    
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    image_dir = os.path.join(BASE_DIR, "rsc/Face Images")
        
    for root, dirs, files in os.walk(image_dir):
        for file in files:
            if file.endswith("png") or file.endswith("jpg") or file.endswith("JPG") or file.endswith("PNG"):#Accept jpg/JPG file types just in case, but they should be in png to prevent compression artefacts from affecting the facial recognition system
                path = os.path.join(root, file)
                label = os.path.basename(os.path.dirname(path))
                ListOfFiles.append(label + "/" +file)
    return ListOfFiles

def GetUserImagePath(ID, imgNum):#Just saves having to type this out all the time
    return ("rsc/Face Images/" + str(ID) + "/" + str(imgNum) + ".png")

def IsUserFaceFolder(ID):#Note Do NOT use ID with leading zeroes since they are not kept
    return os.path.isdir("rsc/Face Images/" + str(ID))#Saves having to type out the file path every time I need this

def IsUserImage(ID, imgNum):#All images in png for quality (compression artefacts from file types such as jpeg could affect recognition)
    #print("we are good")#DEBUG
    if os.path.isfile(GetUserImagePath(ID, imgNum)):
        return True
    elif os.path.isfile("rsc/Face Images/" + str(ID) + "/" + str(imgNum) + ".jpg"):#Accept other file types too
        return True
    elif os.path.isfile("rsc/Face Images/" + str(ID) + "/" + str(imgNum) + ".JPG"):
        return True
    elif os.path.isfile("rsc/Face Images/" + str(ID) + "/" + str(imgNum) + ".PNG"):
        return True
    else:
        return False
                                         
def NextUserImage(ID):
    count = 0
    while(IsUserImage(ID, count)):
        count = count + 1
    #print(count)#DEBUG
    return count
                                         
#Test
#AddUserID(12345)

#Fixed Capture Photo so need new test code (old code used cap, which is bad. Now the func needs to be called everytime for capture)

#Fixed Capture Photo with face detect so no test code to copy over
        
#print(DeleteUserImage(10000, 100))

#print(getImgList())

#print(IsUserFaceFolder(10000))

#print(IsUserImage(10000, 0))

#print(NextUserImage(10000))

#DeleteUSER -TEST-
#print(DeleteUser(10000))

#Capture Photo
#import cv2
#cap=cv2.VideoCapture(0)
#print(CapturePhoto(cap.read()[1],10019))


