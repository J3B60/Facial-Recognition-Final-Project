# Final Year Individual Project - Facial Recognition
## GitHub public release notes
Winpython has been removed in this Github public release (was used to make this project as portable as possible, it came with the included libraries pre-installed to make marking easier)

install Python libraries using:

pip install -r requirements.txt

*Note PyQt5 needs an older version of Spyder so it may need extra work to get it installed. Need to downgrade spyder to 3.3.6

*Uses 7zip-Extra and Imagemagick (Requires PostgreSQL and Python)
You will need to setup Postgresql and rewrite the Stop and Start PostgreSQL batch files to use your installation of PostgreSQL

*Note, the other programs that this face recognition system relies on are 64-bit so use a 64-bit machine and OS. This is better in the case where the system becomes too big (Memory wise) for 32-Bit systems.

*All Usernames and Passwords are case sensitive

Connect a webcam or use a built-in webcam.

## Passwords for the program demo

For Final Project Demonstration/Marking

----------------------------------
Test Account:
Milan=Master Account (Access Level 5)

Username:
Milan

Password:
GzXBTu.a2p3Bc9T

Another Account:
Bob=Access Level 2

Username:
Bob

Password:
hello

----------------------------------
pgAdmin Password: 
Binaries not included in this public Github release, setup your own postgreSQL and pgAdmin

----------------------------------
postgre Server Account: (put these details in the postgreSQL batch files in the "postgresql-windows-x64-binaries" folder)
Host:
localhost

Database:
postgre (default or use your own Database name)

Username:
postgre (default or use your own Database name)

Password:
Use your own postgreSQL password

--------------------------------
Face Images.7z File Password:
File does not exist in this public Github release

## How to run and brief description

Open the _GUI.py programs and run in python.

enrol_GUI.py - Enrol user into system (Creates Employee folder under rsc\FaceImages, adds user to the database, takes photos of the user and retrains the facial recognition system)

manage_GUI.py - Mange every part of the system, from Images, the SQL database, backups and more. See the docs under rsc\doc for everything.

monitor_GUI.py - View the camera feeds and the access history.

security_GUI.py - Detects user face, recognises it and checks whether they have the right permission to access a room then allows or denies access and logs the result in the systems history.

## Documentation and other info

Documentation can be found under \rsc\docs and contain an explanation of all the available functions of the system.

SQL files to create the databases if starting from a fresh PostgreSQL can be found under rsc\sql-files

## Images of the project
### Enrol Program
![enrolGUI](https://user-images.githubusercontent.com/39916226/112058012-ef664180-8b51-11eb-810e-2ee70f95d585.jpg)

### Security Program 
(For access control at the door)
![IdlesecurityGUI](https://user-images.githubusercontent.com/39916226/112057864-be860c80-8b51-11eb-8517-e3a5652af582.png)

### Manage Program
![manageGUI](https://user-images.githubusercontent.com/39916226/112057881-c2199380-8b51-11eb-8cce-d71a55d37f8d.png)

### Monitor Program
![monitorGUI](https://user-images.githubusercontent.com/39916226/112058525-9ba82800-8b52-11eb-8fbc-cfbeada4d69c.png)
