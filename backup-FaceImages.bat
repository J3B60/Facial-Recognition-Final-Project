set YYYY=%date:~6,4%
set MM=%date:~3,2%
set DD=%date:~0,2%

set HH=%time:~0,2%
set MS=%time:~3,2%
set SS=%time:~6,2%

7zip-Extra\7za.exe a "backups/[%DD%-%MM%-%YYYY% %HH%-%MS%-%SS%]Face Images - Backup.7z" "rsc\Face Images\*"