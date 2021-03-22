import subprocess
import os
import platform

def StartPOSTGREsqlServer():
    if platform.system() == 'Windows':
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))#Gets this python file's path excluding file name
        #NOTE __file__ is this python file's path including the file name
        PATH = os.path.join(BASE_DIR, "postgresql-windows-x64-binaries")
        #os.system(PATH)
        subprocess.call('startPOSTGRESQLserver.bat', cwd=PATH, shell=True)
        return True
    else:
        return False#Currently can only start POSTGRESQL windows from windows. Need different platform POSTGRE for other OS


def StopPOSTGREsqlServer():
    if platform.system() == 'Windows':
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))#Gets this python file's path excluding file name
        #NOTE __file__ is this python file's path including the file name
        PATH = os.path.join(BASE_DIR, "postgresql-windows-x64-binaries")
        subprocess.call('stopPOSTGRESQLserver.bat', cwd=PATH, shell=True)
        return True
    else:
        return False#Currently can only stop POSTGRESQL windows from windows. Need different platform POSTGRE for other OS

def StartPgAdmin4():
    if platform.system() == 'Windows':
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))#Gets this python file's path excluding file name
        #NOTE __file__ is this python file's path including the file name
        PATH = os.path.join(BASE_DIR, "postgresql-windows-x64-binaries")
        #os.system(PATH)
        subprocess.call('startPgAdmin4.bat', cwd=PATH, shell=True)
        return True
    else:
        return False#Currently can only start POSTGRESQL windows from windows. Need different platform POSTGRE for other OS

#test
#print(StartPOSTGREsqlServer())
#print(StopPOSTGREsqlServer())
#print(StartPgAdmin4())
