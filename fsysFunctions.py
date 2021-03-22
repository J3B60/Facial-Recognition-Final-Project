import cv2
import os
from PIL import Image
import numpy as np
import math
from matplotlib import pyplot as plt
import random
import statistics
import scipy
from skimage.feature import local_binary_pattern

from sharedFunctions import iniFileParser

ini = iniFileParser('config/shared_config.ini', 'FaceSystem')

#NOTE this function is the result of testing. It fully works and can now be implemented into the program. Below are notes from the testing file
#NOTE this face_detectionNEWER python file is a component rather than the original which is standalone for debugging
#NOTE this face_detectionNEWER is better than face_detectionNEW which has a cap as argument, here we just take the image matrix itself, much easier
#Important differences are:
#- that this takes a image matrix/frame parameter rather than setting as variable in advance
#- no while True Loop, this function will have to be repeatedly called for every frame

#NOTE face_casscade is used by all the functions in this file
face_cascade = cv2.CascadeClassifier('rsc/haar/haarcascade_frontalface_default.xml')#Run once, this runs when the face detection is imported
#Cascade uses grey scale

#The recognizer is used by the face_recog function. The recognizer only needs to be loaded once
recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read("trainner.yml")

#NOTE just returns if a face is found
def face_detectBool(frame):#takes frame (a matrix/array)
    global  face_cascade
    grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)#detect in grey but show colour
    faces = face_cascade.detectMultiScale(frame, 1.3, 5)#Numbers are threashold(scale factor, minNeighbours)
    for (x,y,w,h) in faces:
        #cv2.rectangle(frame, (x,y), (x+w, y+h), (255,0,0), 2)#255 is blue, 2 is line width#roi=region of interest
        return True#Found a face
    return False
        #find stuff within face like eye goes here grey[y:y+h, x:x+w], frame[y:y+h, x:x+h] then for..
        #Want to save the frame only when detected

#NOTE this function is the result of testing. Below are comments from the test .py files
#NOTE this face_detectionNEWER python file is a component rather than the original which is standalone for debugging
#NOTE this face_detectionNEWER is better than face_detectionNEW which has a cap as argument, here we just take the image matrix itself, much easier
#Important differences are:
#- that this takes a image matrix/frame parameter rather than setting as variable in advance
#- no while True Loop, this function will have to be repeatedly called for every frame
def face_detectFB(frame):#Gives Frame with the Face highlighted(ie has a box around it)
    global  face_cascade
    grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)#detect in grey but show colour
    faces = face_cascade.detectMultiScale(frame, 1.3, 5)#Numbers are threashold(scale factor, minNeighbours)
    for (x,y,w,h) in faces:
        cv2.rectangle(frame, (x,y), (x+w, y+h), (255,0,0), 2)#255 is blue, 2 is line width#roi=region of interest
        #Found a face
    return frame
        #find stuff within face like eye goes here grey[y:y+h, x:x+w], frame[y:y+h, x:x+h] then for..
        #Want to save the frame only when detected

def face_detectROI(frame):#Gives Frame with the Face highlighted(ie has a box around it)
    global  face_cascade
    grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)#detect in grey but show colour
    faces = face_cascade.detectMultiScale(frame, 1.3, 5)#Numbers are threashold(scale factor, minNeighbours)
    for (x,y,w,h) in faces:
        return grey[y:y+h, x:x+w]#ROI
    return None
        #find stuff within face like eye goes here grey[y:y+h, x:x+w], frame[y:y+h, x:x+h] then for..
        #Want to save the frame only when detected

#Note the original .py function failed doing the training properly since the line roi = image_array[y:y+h,x:x+2] was x:x+2 instead of x:x+w (it was an accident code was actually working fine)

def face_recog_train():
    global face_cascade
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    image_dir = os.path.join(BASE_DIR, "rsc/Face Images")

    recognizerTrain = cv2.face.LBPHFaceRecognizer_create()

    y_labels = []
    x_train = []

    for root, dirs, files in os.walk(image_dir):
        for file in files:
            if file.endswith("png") or file.endswith("jpg") or file.endswith("JPG") or file.endswith("PNG"):
                path = os.path.join(root, file)
                label = os.path.basename(os.path.dirname(path))
                #print(label, path)#DEBUG
            
                pil_image = Image.open(path).convert("L")
                image_array = np.array(pil_image, "uint8")
                #print(image_array)#DEBUG

                #NOTE NEED TO MESS AROUND WITH THE detectMultiScale() Parameters to get best results (1.3, 5) is the old magic combination, another good one is (1.5, 5). Using default results in more of the lower quality images being used (hence bigger trainner.yml files). Need to actually test what is best.
                faces = face_cascade.detectMultiScale(image_array)#, 1.3,5)#So unlike face_detection_bool, this has no cv2.cvtColor so this is a remake of the function otherwise they work the same
                for (x,y,w,h) in faces:
                    roi = image_array[y:y+h, x:x+w]
                    x_train.append(roi)
                    y_labels.append(int(label))

    if not x_train == []:
        recognizerTrain.train(x_train, np.array(y_labels))
        recognizerTrain.save("trainner.yml")
        return True#Finished
    else:
        return False#ERROR, no Images/Users in 'Face Images' folder


def face_recog(frame):
        global  face_cascade
        global recognizer
        grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)#OpenCV will automatically change frame to Greyscale where needed
        faces = face_cascade.detectMultiScale(grey, 1.3, 5)#Numbers are threashold(scale factor, minNeighbours)
        for (x,y,w,h) in faces:
            return recognizer.predict(grey[y:y+h, x:x+w])#roi_grey = grey[y:y+h, x:x+w] # Returns Label and confidence [0],[1]
            #if confidence>=45 and confidence <=85:#You want the image with max confidence which it does, we can set a threashold of confidence with this if statement. Will need testing to get the right value.
        return None#Otherwise None

#Default threshold to 80, need to do some testing for my cameras to find the best setting. Threshold will vary betweeb scenarios so this option will be open for management
def face_recog_decision(face_recog_ret, threshold=int(ini['face_recog_threshold'])):
    if face_recog_ret[1] > threshold:
        return face_recog_ret[0]
    else:
        return None
    

#################################################################################   ANTI-SPOOF   #######################################################################

#FOR FOURIER ANTI-SPOOF METHOD
def ImgFFT(frame):#Image Fast Fourier Transform
    imgOUT = np.fft.fft2(frame)
    imgReal = 1*np.log(1+np.abs(np.fft.fftshift(imgOUT)))
    #plt.imshow(imgReal, cmap = 'gray')#Visual Output#DEBUG
    #plt.show()#DEBUG
    return imgReal

#FOR FOURIER ANTI-SPOOF METHOD
def HPF(frame):#HighPassFilter
    yAx = np.linspace(-math.ceil(frame.shape[0]/2), math.floor(frame.shape[0]/2)-1, frame.shape[0])
    xAx = np.linspace(-math.ceil(frame.shape[1]/2), math.floor(frame.shape[1]/2)-1, frame.shape[1])
    x, y = np.meshgrid(xAx,yAx)
    z = np.sqrt(np.power(x,2) + np.power(y,2))#Circle equation
    if frame.shape[0] < frame.shape[1]:#Need to pick the smaller axis
        circle = z> (((frame.shape[0]*2)/3)/2)#So get 2/3 of Foureir specturm then divide by 2 to get radius rather than diameter
    else:
        circle = z> (((frame.shape[1]*2)/3)/2)#So get 2/3 of Foureir specturm then divide by 2 to get radius rather than diameter
    imgOUT = frame * circle
    #plt.imshow(imgOUT, cmap = 'gray')#Visual Output#DEBUG
    #plt.show()#DEBUG
    return imgOUT

#FOR FOURIER ANTI-SPOOF METHOD
#Returns N random sample indexs. NOTE Samples without replacement
#NOTE research paper uses frameSet_Size of 10 and 3 random samples
def frameSetSample(frameSet_Size, NumOfSamples, replacement):
    samples = []
    while(len(samples) != NumOfSamples):
        if replacement:
            samples.append(random.randint(1,frameSet_Size)-1)
        else:
            tempSamp = random.randint(1,frameSet_Size)-1
            if tempSamp not in samples:
                samples.append(tempSamp)
    return samples

#FOR FOURIER ANTI-SPOOF METHOD
#OLD - Here just incase needed
#Standard, just like research paper. No customizability
#def OLDframeSetSample():
#    r1 = random.randint(1,10)-1#select 3 frames at random #NOTE randin, lowest num not included so 1-10 then minus 1 to get 0-9
#    r2 = r1#guarantees the while loop run at least once
#    while (r2 == r1):
#        r2 = random.randint(1,10)-1
#    r3 = r2#same thing here
#    while (r3 == r2 or r3 == r1):
#        r3 = random.randint(1,10)-1
#    return (r1,r2,r3)

#FOURIER ANTI-SPOOF PART 1
#High Freqeuncy Descriptor
def HFD(frameSet, NumOfSamples=int(ini['hfd_numofsamples']), replacement=int(ini['hfd_replacement'])):#Default to research standard. Defaults are frameSet_Size=10, NumOfSamples=3, replacment=False
    sampleIndex = frameSetSample(len(frameSet), NumOfSamples, replacement)
    listOfHFD = []#High Frequency Descriptors List
    for index in sampleIndex:
        FREQspec = ImgFFT(frameSet[index])
        FCS = FREQspec.sum()#Forier Coefficient Sum #ie the energy value for the image aka the total energy
        HPF_FREQspec = HPF(FREQspec)#Note this also includes all 0 values too, so it's not good for averaging/standard devidation/mean because 0's will skew the result
        HFFCS = HPF_FREQspec.sum()#High Frequency Fourier Coefficient Sum
        HFD = (FCS/HFFCS) * 1000
        listOfHFD.append(HFD)#To find median
        #listOfFREQspec.append(FREQspec)
    medianOfHFD = statistics.median(listOfHFD)
    return medianOfHFD

#FOURIER ANTI-SPOOF PART 2
#Frequency Dynamics Descriptor
#Default, finds STD of every 4 images just like research paper
def FDD(frameSet, step=int(ini['fdd_step'])):#Default step = 4
    listOfFCS = []
    for index in range(0, len(frameSet), step):#Every 4 images
        FREQspec = ImgFFT(frameSet[index])#Computationaly expensive to run live on my laptop for all images in real time so if this antispoof technique works then I may need to use a subset of the camerafeed frames rather than processing every 10 frames
        FCS = FREQspec.sum()
        listOfFCS.append(FCS)
    FDD = statistics.stdev(listOfFCS)#ie the stdOfFCSs
    #print(FDD)#DEBUG
    return FDD
    #if FDD > #someThreshold: #Real Face else: Fail/Fake Face#THIS CAN BE DONE OUTSIDE THIS FUNCTION

#FOURIER ANTI-SPOOF Decision Part 1 - HFD
#Defaults that are based on the default settings of HFD() function, Note that the threshold will change depending on a number of factors
#Default Threshold based on research paper, need to do some testing to get best results for my cameras
def HFD_Decision(medianOfHFD, threshold=int(ini['hfd_threshold'])):#Default 1.45x10^4
    if medianOfHFD > threshold:
        return True
    else:
        return False

#FOURIER ANTI-SPOOF Decision Part 2 - FDD
#Defaults based on the default settings of FDD() function, Note that the threshold will change depending on a number of factors
#Default Threshold based on research paper, need to do some testing to get best results for my cameras.
def FDD_Decision(FDD, threshold=int(ini['fdd_threshold'])):#Default 900
    if FDD > threshold:
        return True
    else:
        return False

#BLINK DETECTION - NOT USED
eye_cascade = cv2.CascadeClassifier('rsc/haar/haarcascade_eye.xml')#Detects Open Eyes
Leye_cascade = cv2.CascadeClassifier('rsc/haar/haarcascade_lefteye_2splits.xml')#Detects Open&closed Left Eyes
Reye_cascade = cv2.CascadeClassifier('rsc/haar/haarcascade_righteye_2splits.xml')#Detects Open&closed Right Eyes
def detect_blink(img):#VERY HIGH FAIL RATE SO IT'S NOT USED, note this is not the function that is used by main program for RealFace decision
    global face_cascade
    global eye_cascade
    global Leye_cascade
    global Reye_cascade
    left_Open = None
    right_Open = None
    Reyes_both = Reye_cascade.detectMultiScale(roi_grey)##Set some limits otherwise it is bad
    Leyes_both = Leye_cascade.detectMultiScale(roi_grey)
    for (ex,ey,ew,eh) in Reyes_both:
        roi_Reye_grey = roi_grey[ey:ey+eh, ex:ex+ew]
        eyes_open = eye_cascade.detectMultiScale(roi_Reye_grey)
        if type(eyes_open) == tuple:
            right_Open = False
        else:
            for (ex2,ey2,ew2,eh2) in eyes_open:
                right_Open = True
    for (ex3,ey3,ew3,eh3) in Leyes_both:
        roi_Leye_grey = roi_grey[ey3:ey3+eh3, ex3:ex3+ew3]
        eyes_open = eye_cascade.detectMultiScale(roi_Leye_grey)
        if type(eyes_open) == tuple:
            left_Open = False
        else:
            for (ex2,ey2,ew2,eh2) in eyes_open:
                left_Open = True
    return (left_Open, right_Open)

def detect_blink_decision(face_roi_grey_img_set):#This is the actual funtion used in main programs not the detect_blink
    retSet = []
    OepnCount = 0
    ClosedCount = 0
    for roi_grey in face_roi_grey_img_set:
        retSet.append(detect_blink(roi_grey))
    for i in retSet:
        if i==(True, True):
            OpenCount = OpenCount + 1
        if i==(False, False):
            ClosedCount = ClosedCount + 1
    if ClosedCount < 5 and OpenCount > 2:#WE want some blink frames and some open frames#Trial and error tuning
        return True#Real Face
    else:
        return False#Real Face not detected

#COLOUR TEXTURE ANALYSIS
radius = 1
n_points = 8#Neighbours
method = 'default'
CTAThreshold = 5000
def CTA_decision(img, label):#label is the face recognisers label, this runs after face recog
    global CTAThreshold
    #FIRST THE INPUT IMG
    inIMGlbphALL = CTA_lbph(img)

    randIMG = random.choice(os.listdir("rsc\\Face Images\\" + str(label) + "\\"))#Pick a random enroll img as reference
    refIMG = cv2.imread("rsc\\Face Images\\"+ str(label) +"\\" + str(randIMG), cv2.IMREAD_COLOR)#load ref img

    refIMGlbphALL = CTA_lbph(refIMG)

    if scipy.stats.chisquare(inIMGlbphALL,refIMGlbphALL)[0] < CTAThreshold: ##########################################Threshold
        return True
    else:
        return False
    
def CTA_lbph(img):
    global radius
    global n_points
    global method
    yCbCrIMG = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb)#Convert to YCbCr
    lbpY = local_binary_pattern(yCbCrIMG[:,:,0], n_points, radius, method)#Y-Channel
    lbpCb = local_binary_pattern(yCbCrIMG[:,:,1], n_points, radius, method)#Cb-Channel
    lbpCr = local_binary_pattern(yCbCrIMG[:,:,2], n_points, radius, method)#Cr-Channel

    nbins = int(lbpY.max() + 1)#Bins

    lbphY, _ = np.histogram(lbpY, nbins)#Histogram Y
    lbphCb, _ = np.histogram(lbpCb, nbins)#Histogram Cb
    lbphCr, _ = np.histogram(lbpCr, nbins)#Histogram Cr
    return np.concatenate((lbphY,lbphCb, lbphCr))#Result, ready for comparison
    

#TEST
if __name__ == "__main__":
    #print(ini)#DEBUG

    #Test
    #print(face_recog_train())

    #Test
    #cap = cv2.VideoCapture(0)
    #while(True):
    #    frame = cap.read()[1]
    #    print(face_recog(frame))


    pass
