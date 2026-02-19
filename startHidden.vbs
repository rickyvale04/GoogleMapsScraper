' Google Maps Scraper - Silent Launcher for Windows
' Double-click this file to start the server without showing a terminal window.
' The browser will open automatically when the server is ready.

Set objShell = CreateObject("WScript.Shell")
Set objFSO = CreateObject("Scripting.FileSystemObject")

' Go to the script's directory
strScriptDir = objFSO.GetParentFolderName(WScript.ScriptFullName)
objShell.CurrentDirectory = strScriptDir

' Check if Python is available
Dim pythonCmd
pythonCmd = ""
On Error Resume Next
objShell.Run "python --version", 0, True
If Err.Number = 0 Then
    pythonCmd = "python"
Else
    Err.Clear
    objShell.Run "python3 --version", 0, True
    If Err.Number = 0 Then
        pythonCmd = "python3"
    End If
End If
On Error Goto 0

If pythonCmd = "" Then
    MsgBox "Python non trovato!" & vbCrLf & vbCrLf & "Installa Python 3.8+ da python.org" & vbCrLf & "Assicurati di selezionare 'Add Python to PATH'", vbCritical, "Google Maps Scraper"
    WScript.Quit 1
End If

' Check if the server is already running
On Error Resume Next
Dim objHTTP
Set objHTTP = CreateObject("MSXML2.XMLHTTP")
objHTTP.Open "GET", "http://localhost:5001/health", False
objHTTP.Send
If objHTTP.Status = 200 Then
    ' Server already running, just open browser
    objShell.Run "http://localhost:5001"
    WScript.Quit 0
End If
On Error Goto 0

' Start the server silently (window style 0 = hidden)
strLogFile = objFSO.BuildPath(strScriptDir, ".server.log")
objShell.Run pythonCmd & " api_server.py > """ & strLogFile & """ 2>&1", 0, False

' Wait for server to be ready (poll /health, max 30 seconds)
Dim i, serverReady
serverReady = False
For i = 1 To 30
    WScript.Sleep 1000
    On Error Resume Next
    Set objHTTP = CreateObject("MSXML2.XMLHTTP")
    objHTTP.Open "GET", "http://localhost:5001/health", False
    objHTTP.Send
    If Err.Number = 0 And objHTTP.Status = 200 Then
        serverReady = True
        Exit For
    End If
    On Error Goto 0
Next

' Open browser
If serverReady Then
    objShell.Run "http://localhost:5001"
Else
    MsgBox "Il server non si e' avviato in tempo." & vbCrLf & vbCrLf & "Controlla .server.log per dettagli.", vbExclamation, "Google Maps Scraper"
End If
