:: Create the libraries folder in case it does not exist
mkdir -p "C:\%HOMEPATH%\Documents\Arduino\libraries"
:: Remove previous bitbloqLibs
RD /S /q "C:\%HOMEPATH%\Documents\Arduino\libraries\bitbloqLibs"

::INSTALL WGET FIRST!!! / ADD it in this path 
"%~dp0\wget64.exe" https://github.com/bq/bitbloqLibs/archive/master.zip --no-check-certificate
"%~dp0\7za.exe" x master.zip
DEL master.zip
rename bitbloqLibs-master bitbloqLibs
MOVE bitbloqLibs "C:\%HOMEPATH%\Documents\Arduino\libraries\"
RD /S /q bitbloqLibs

::Remove all exes as well:
DEL wget*
DEL 7zxa.*

::Add the .reg file
regedit.exe /S src/res/web2board.reg
timeout 300