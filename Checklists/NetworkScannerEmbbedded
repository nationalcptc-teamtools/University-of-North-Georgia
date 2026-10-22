Keep track of network and do enumeration and exploitation on embedded services. 



1. Nmap scan the provided subnets, output and upload results.
```
nmap -A --top-ports 100 -vvv 192.168.1.0/24 -oA subnetscan
```
	1. Specifically out of scope machines?
```
sudo nmap -A --top-ports 100 -vvv 192.168.1.0/24 --exclude 192.9.9.9 -oA subnetscan
```
2. Report hosts
3. Start Scanning Hosts Communicate Finds (UDP scan if needed )
```
nmap -sV -p- -A -T4   192.168.1.10 -oA #########
```
# other roles to report to 
- windows
- linux
-  web/ai 
 
4. Investigate non standard (probably embedded) for the following.
	1. cmd injection
	2. auth bypass
	3. printf
	4. probably not overflows
# post 
1. make network diagram draw.io
