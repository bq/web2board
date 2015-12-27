IF EXIST "%PROGRAMFILES(X86)%" (regedit.exe /S res/web2board.reg) ELSE (regedit.exe /S res/web2boardTo32.reg)


START Web2Board.exe

PAUSE