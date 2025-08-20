' run_bot.vbs — тихий запуск бота с правильной рабочей папкой
Option Explicit

Dim fso, shell, scriptDir, py, cmd
Set fso   = CreateObject("Scripting.FileSystemObject")
Set shell = CreateObject("WScript.Shell")

' Папка, где лежит этот VBS
scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)

' !!! Укажи путь к pythonw.exe, если он не в PATH:
py = """C:\Users\User\AppData\Local\Programs\Python\Python310\pythonw.exe"""
' или, если Python в PATH, можно просто:
' py = "pythonw"

' Делаем рабочую папку как у скрипта (важно для JSON и аватарок)
shell.CurrentDirectory = scriptDir

' Команда запуска
cmd = py & " " & """" & scriptDir & "\bot.py" & """"

' 0 — без окна, False — не ждать завершения
shell.Run cmd, 0, False
