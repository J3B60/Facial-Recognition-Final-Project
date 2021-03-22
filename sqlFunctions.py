import psycopg2
from passlib.hash import pbkdf2_sha256

#NOTES: These notes are information regarding the differences between the functions in this sqlFunctions.py file and the original seperate .py function files.
#-The defualt psycopg2.connect() login information has been replaced with db, which takes the information found from the database.ini file about the login information.

#NOTE changed db from parameter to global variable. The database.ini file is now loaded when this .py file is imported sinceit makes more sense and makes life easier.

from sharedFunctions import iniFileParser

db = iniFileParser("config/database.ini", "postgresql")
ini = iniFileParser("config/shared_config.ini", "sqlFunctions")

def CheckUserCredentials(UserName, PassWord):#Username and Password will be checked against database
    global db
    UserList = SHOWtable("usercredentials")
    for Entry in UserList:
        if Entry[3] == UserName:#Find correct entry using UserName
            if pbkdf2_sha256.verify(PassWord,Entry[2]):#Check Hashed Pwd
                return Entry[1]#Return Access Level
            else:
                return 0#Bad PWD
    else:
        return 0#0 Corresponds to No-access to system/Not permitted

def TestPOSTGREsqlServer():#Test connection to server
    global db
    count = 0
    for i in range(10):#Give it 10 tries to connect
        try:
            conn = psycopg2.connect(host=db['host'], database=db['database'], user=db['user'], password=db['password'])
            break
        except:
            count = count + 1
    if not count == 10:
        return True
    else:
        return False#All connections failed

def DELETEentry(table,condition):#Generic for any table
    global db
    conn = psycopg2.connect(host=db['host'], database=db['database'], user=db['user'], password=db['password'])
    cur = conn.cursor()
    try:
        cur.execute('DELETE FROM public.'+ table +' WHERE '+ condition)
    except:
        cur.close()
        conn.close()    
        return False#Failed: BuildingID Might not be unique
    #id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()    
    return True#success

def UPDATEentrySimple(tableNAME, tableSET, tableCondition):#INSERT but Generic, TableName is string, tableVALUES is tuple
    global db
    conn = psycopg2.connect(host=db['host'], database=db['database'], user=db['user'], password=db['password'])
    cur = conn.cursor()

    #-- Test connect to Table + sets cursor position in table--
    #try:
    #    cur.execute('SELECT * FROM public.' + tableNAME)#To get columns ##NOTE Dont actually need *, just need first value so inefficient
    #except:
    #    cur.close()
    #    conn.close()
    #    return (False,False)#TableName invalid/doesnt Exist

    #--Executing the UPDATE--
    try:
        cur.execute('UPDATE public.' + tableNAME + ' SET ' + tableSET + ' WHERE ' + tableCondition)
    except:
        cur.close()
        conn.close()    
        return False#(True,False)#Failed: BuildingID Might not be unique
    conn.commit()
    cur.close()
    conn.close()    
    return True#(True,True)#success

def INSERTentry(tableNAME, tableVALUES):#INSERT but Generic, TableName is string, tableVALUES is tuple
    global db
    conn = psycopg2.connect(host=db['host'], database=db['database'], user=db['user'], password=db['password'])
    cur = conn.cursor()
    try:
        cur.execute('SELECT * FROM public.' + tableNAME)#To get columns ##NOTE Dont actually need *, just need first value so inefficient
    except:
        cur.close()
        conn.close()
        return False#(False,False,False)#TableName invalid/doesnt Exist
    buildSLEN = len(tableVALUES)#Number of Values
    if not (buildSLEN) == len(cur.fetchone()):
        cur.close()
        conn.close()
        return False#(True,False,False)#Not enough values for the columns
    buildS = '%s' #The number of values will be (and must be) at least be 1
    for i in range(buildSLEN-1):
        buildS = buildS + ",%s"
    try:
        cur.execute('INSERT INTO ' + tableNAME + ' VALUES (' + buildS + ')', tableVALUES)
    except:
        cur.close()
        conn.close()    
        return False#(True,True,False)#Failed: BuildingID Might not be unique
    conn.commit()
    cur.close()
    conn.close()    
    return True#(True,True,True)#success

def SHOWcolumnNames(tableName):#Outputs list of names as string (not tuple as usual) e.g: ['col1','col2','col3',...]
    global db
    OUTlist = []
    conn = psycopg2.connect(host=db['host'], database=db['database'], user=db['user'], password=db['password'])
    cur = conn.cursor()
    try:
        cur.execute('SELECT * FROM public.' + tableName + ' LIMIT 1')
    except:
        cur.close()
        conn.close()    
        return OUTlist#Failed
    for i in range(len(cur.fetchone())):
        OUTlist.append(cur.description[i][0])
    conn.commit()
    cur.close()
    conn.close()    
    return OUTlist#success 

def SHOWtable(tableName):
    global db
    OUTlist = []
    conn = psycopg2.connect(host=db['host'], database=db['database'], user=db['user'], password=db['password'])
    cur = conn.cursor()
    try:
        cur.execute('SELECT * FROM public.' + tableName)
    except:
        cur.close()
        conn.close()    
        return OUTlist#Failed: eg.Table doesn't exist/Postgre server not on??
    for tableItem in cur.fetchall():
        OUTlist.append(tableItem)
    conn.commit()
    cur.close()
    conn.close()    
    return OUTlist#success    

def SHOWtableList():
    global db
    OUTlist = []
    conn = psycopg2.connect(host=db['host'], database=db['database'], user=db['user'], password=db['password'])
    cur = conn.cursor()
    try:
        cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_type='BASE TABLE';")
    except:
        cur.close()
        conn.close()    
        return OUTlist#Failed: No tables in Database/Postgre server not on??
    for tableItem in cur.fetchall():
        OUTlist.append(tableItem[0])#Note the [0], just taking the first column, we only get one column anyway from cur.execute SQL statment
    conn.commit()#Don't think I need to commit but just incase, to have a proper close, maybe postgre logs all SQL execution
    cur.close()
    conn.close()    
    return OUTlist#success 

def UPDATEentry(tableNAME, tableVALUES, tableCondition):#INSERT but Generic, TableName is string, tableVALUES is tuple
    global db
    conn = psycopg2.connect(host=db['host'], database=db['database'], user=db['user'], password=db['password'])
    cur = conn.cursor()

    #-- Test connect to Table + sets cursor position in table--
    try:
        cur.execute('SELECT * FROM public.' + tableNAME)#To get columns ##NOTE Dont actually need *, just need first value so inefficient
    except:
        cur.close()
        conn.close()
        return False#(False,False,False)#TableName invalid/doesnt Exist

    #--Checking number of values valid--
    buildSLEN = len(tableVALUES)#Number of Values
    if not (buildSLEN) == len(cur.fetchone()):
        cur.close()
        conn.close()
        return False#(True,False,False)#Not enough values for the columns

    #--Column Names--
    LISTcolNames = SHOWcolumnNames(tableNAME)
    SETlistBuild = ''
    for i in range(len(LISTcolNames)):
        SETlistBuild = SETlistBuild + '"' + ListcolNames[i] + '"=%s, '
        
    #--Executing the UPDATE--
    try:
        cur.execute('UPDATE public.' + tableNAME + ' SET ' + SETlistBuild + ' WHERE ' + tableCondition, tableVALUES)
    except:
        cur.close()
        conn.close()    
        return False#(True,True,False)#Failed: BuildingID Might not be unique
    conn.commit()
    cur.close()
    conn.close()    
    return True#(True,True,True)#success

def EXECUTEsqlFile(SQLstring):
    global db
    conn = psycopg2.connect(host=db['host'], database=db['database'], user=db['user'], password=db['password'])
    cur = conn.cursor()
    try:
        cur.execute(SQLstring)
    except:
        cur.close()
        conn.close()
        return False#Executing SQL failed (Invalid File or does not exist)
    conn.commit()
    cur.close()
    conn.close()
    return True#Executing SQL file successful

def COPYtable(tableName, outputFileName, colNameList=None, delimiter=ini['csv_delimiter']):
    global db
    colString = ""
    if colNameList != None:
        colString = "("
        for col in colNameList:
            colString = colString + col + ","
        colString = colString[0:len(colString)-1]
        colString = colString + ")"
    conn = psycopg2.connect(host=db['host'], database=db['database'], user=db['user'], password=db['password'])
    cur = conn.cursor()
    try:
        cur.execute("COPY public." + tableName + " " + colString + " TO  '"+ outputFileName + "' DELIMITER '" + delimiter + "';")
    except:
        cur.close()
        conn.close()
        return False#Executing SQL failed (Invalid File or does not exist)
    conn.commit()
    cur.close()
    conn.close()
    return True#Executing SQL file successful

def SHOWuserAccess(userID):
    global db
    OUTlist = []
    conn = psycopg2.connect(host=db['host'], database=db['database'], user=db['user'], password=db['password'])
    cur = conn.cursor()
    try:
        cur.execute('SELECT "RoomID" FROM public.access WHERE "UserID" = ' + str(userID))
    except:
        cur.close()
        conn.close()    
        return OUTlist#Failed: eg.Table doesn't exist/Postgre server not on??
    for tableItem in cur.fetchall():
        OUTlist.append(tableItem[0])
    conn.commit()
    cur.close()
    conn.close()    
    return OUTlist#success 

def APPENDcameraLog(accessStatus, cameraID, userID):
    global db
    conn = psycopg2.connect(host=db['host'], database=db['database'], user=db['user'], password=db['password'])
    cur = conn.cursor()
    try:
        cur.execute('UPDATE public.camera SET "CameraInfo"= "CameraInfo" || ' + "E'\\n " + str(accessStatus)+ " to User " + str(userID) + "'" + ' WHERE "CameraID" = ' +str(cameraID))
    except:
        cur.close()
        conn.close()    
        return False#Failed: eg.Table doesn't exist/Postgre server not on??
    conn.commit()
    cur.close()
    conn.close()    
    return True#success 

if __name__ == "__main__":
    #from pgFunctions import *
    #StartPOSTGREsqlServer()
    #test
    #print(CheckUserCredentials('Milan', 'GzXBTu.a2p3Bc9T'))#Expected: 5
    #print(CheckUserCredentials('Milan', 'GzXBTu.a2p3Bc9TUBAGUBA'))#Expected: Fail
    #print(CheckUserCredentials('Milannn', 'GzXBTu.a2p3Bc9T'))#Expected: Fail
    #print(CheckUserCredentials('Bob', 'hello'))#Expected: 2

    #print(TestPOSTGREsqlServer())

    #print(DELETEentry("building",10))#Table, ID

    #test - NEED TO CHANGE, THIS IS JUST A COPY OF UPDATE ENTRY
    #print(UPDATEentrySimple("camera", (100, "test3", "http://192.168.2.5:4747/mjpegfeed?960x720", 3, "This is to test the AddCameraFunctionTEST3")))#tableName
    #print(UPDATEentrySimple("building",(15, "testB15", "This is to test the generic INSERTentry function")))
    #print(UPDATEentrySimple("access", (10000, 100)))
    #print(UPDATEentrySimple("department",(0, 10, "testD0", "This is to test the AddDepartmentFunction")))
    #print(UPDATEentrySimple("userface", (10000, "Milan", "Lacmanovic")))
    #print(UPDATEentrySimple("room", (100, 0, "testR0", "This is to test the AddRoomFunction")))
    #print(UPDATEentrySimple("usercredentials", (10000, 5, "2manGz48xfPxrYz", "Milan", "This is to test the AddUserCredentialsFunction")))

    #print(INSERTentry("camera", (100, "test3", "http://192.168.2.5:4747/mjpegfeed?960x720", 3, "This is to test the AddCameraFunctionTEST3")))#tableName
    #print(INSERTentry("building",(15, "testB15", "This is to test the generic INSERTentry function")))
    #print(INSERTentry("access", (10000, 100)))
    #print(INSERTentry("department",(0, 10, "testD0", "This is to test the AddDepartmentFunction")))
    #print(INSERTentry("userface", (10000, "Milan", "Lacmanovic")))
    #print(INSERTentry("room", (100, 0, "testR0", "This is to test the AddRoomFunction")))
    #print(INSERTentry("usercredentials", (10000, 5, "2manGz48xfPxrYz", "Milan", "This is to test the AddUserCredentialsFunction")))

    #print(SHOWcolumnNames("camera"))#tableName

    #print(SHOWtable("usercredentials"))#tableName

    #print(UPDATEentry("camera", (100, "test3", "http://192.168.2.5:4747/mjpegfeed?960x720", 3, "This is to test the AddCameraFunctionTEST3")))#tableName
    #print(UPDATEentry("building",(15, "testB15", "This is to test the generic INSERTentry function")))
    #print(UPDATEentry("access", (10000, 100)))
    #print(UPDATEentry("department",(0, 10, "testD0", "This is to test the AddDepartmentFunction")))
    #print(UPDATEentry("userface", (10000, "Milan", "Lacmanovic")))
    #print(UPDATEentry("room", (100, 0, "testR0", "This is to test the AddRoomFunction")))
    #print(UPDATEentry("usercredentials", (10000, 5, "2manGz48xfPxrYz", "Milan", "This is to test the AddUserCredentialsFunction")))

    #NO TEST STATEMENTS FOR EXECUTEsqlFile()


    #SHOW TABLE TEST DB ###########OLD, NOT VALID, USES DB AS GLOBAL VARIABLE
    #db = {'host': 'localhost', 'database': 'postgres', 'user': 'postgres', 'password': '7E3LqYdZKiDMe38'}
    #print(SHOWtable("usercredentials", db))

    #SHOW TABLE LIST
    #print(SHOWtableList())

    #COPY Table
    #print(COPYtable('camera', "C:/Users/milan/OneDrive - University of Reading/UoR Y3/CS3IP16/PROGRAM/Camera-Copytest.csv"))

    #SHOWuserAccess
    #print(SHOWuserAccess(10000))

    #APPENDcameraLog
    #print(APPENDcameraLog("[DD-MM-YYYY HH:MM:SS] ACCESS-GRANTED", 3, 10000))
    
    pass
