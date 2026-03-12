Set WshShell = CreateObject("WScript.Shell")

WshShell.CurrentDirectory = "C:\Users\User\Dev\h"

WshShell.Run """C:\Users\User\AppData\Local\Programs\Python\Python313\pythonw.exe"" update_local.py", 0, True