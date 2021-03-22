#Postgresql 12.1.1
Edit these batc files if you are using your own postgreSQL (PostgreSQL binaries are not included in this Github Public release)
.\bin\initdb.exe -D .\pgdata -U postgres -W -E UTF8 -A scram-sha-256
#Things need to run from here inorder to use the .\pgdata folder where everything is stored
#To start server
.\pg_ctl.exe -D .\pgdata start

#To stop server
.\pg_ctl.exe -D .\pgdata stop

.\bin\psql.exe found in bin, 
.\pgAdmin\bin\pgAdmin4.exe and pgAdmin4 is in "pgAdmin 4\bin"