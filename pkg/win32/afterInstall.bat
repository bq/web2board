:: Create the libraries folder in case it does not exist
mkdir -p "C:\%HOMEPATH%\Documents\Arduino\libraries"
:: Remove previous bitbloqLibs
RD /S /q "C:\%HOMEPATH%\Documents\Arduino\libraries\bitbloqLibs"

::INSTALL WGET FIRST!!! / ADD it in this path 
"%~dp0\wget.exe" https://github.com/bq/bitbloqLibs/archive/v0.0.1.zip --no-check-certificate

:CheckOS
IF EXIST "%PROGRAMFILES(X86)%" (GOTO 64BIT) ELSE (GOTO 32BIT)

:64BIT
echo 64-bit...
"%~dp0\7za-64.exe" x v0.0.1.zip
GOTO END

:32BIT
echo 32-bit...
"%~dp0\7za-32.exe" x v0.0.1.zip
GOTO END

:END

DEL v0.0.1.zip
rename bitbloqLibs-0.0.1 bitbloqLibs
MOVE bitbloqLibs "C:\%HOMEPATH%\Documents\Arduino\libraries\"
RD /S /q bitbloqLibs

::Remove all exes as well:
DEL wget*
DEL 7zxa.*

::Add the .reg file
::CheckOS
IF EXIST "%PROGRAMFILES(X86)%" (regedit.exe /S src/res/web2board.reg) ELSE (regedit.exe /S src/res/web2boardTo32.reg)
