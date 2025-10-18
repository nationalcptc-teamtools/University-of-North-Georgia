#!/bin/bash
###########################################################################
###									###
### 	Written by: 	Hoshtoo						###
###                                                          		###
### 	Description: 	Starting script made by the 			###
### 			HackHawks for use at the Collegiate		### 
### 			Penetration Testing Competition          	###
###									###
###########################################################################

if [ ${#1} -ge 7 ]; then
	mkdir upload
	sudo -v
	echo -e "\033[32mStarting nmap full port scan on $1\033[0m"
	sudo nmap --stats-every 5s -p- -O $1 -oN upload/nmap_$1_tcpFullPorts.txt -oX nmap_$1_tcpFullPorts.xml
	sudo chmod 666 upload/nmap_$1_tcpFullPorts.txt
	sudo chmod 666 nmap_$1_tcpFullPorts.xml
	ports=$(cat nmap_$1_tcpFullPorts.xml | grep '<port protocol="tcp" portid="' | grep 'state="open"' | cut -d'"' -f4 | paste -sd,)
	echo -e "\033[32mPorts: $ports\033[0m"
	cmds=()
	if [ -n "$ports" ]; then
		cmds+=("./nmaps.sh $1 $ports")
	fi
	if [[ ",$ports," == *",21,"* ]]; then
		cmds+=("./ftp.sh $1")
	fi
	if [[ ",$ports," == *",80,"* ]] || [[ ",$ports," == *",443,"* ]] || [[ ",$ports," == *",8080,"* ]] || [[ ",$ports," == *",8000,"* ]]; then
		cmds+=("./hawkeye.sh $1")
	fi
	if grep -q "OS: Windows" "upload/nmap_$1_tcpFullPorts.txt"; then
		cmds+=("./extras.sh $1")
	fi

	echo -e "\033[32m[+] Commands to run:\033[0m"
	for c in "${cmds[@]}"; do
		echo "    $c"
	done
	
	mprocs_args=()
	for s in "${cmds[@]}"; do
		mprocs_args+=("$s")
	done
	mprocs "${mprocs_args[@]}"

else
	echo -e "\033[31m$1 is not a valid IP address\033[0m"
fi

sudo rm nmap_$1_udpCommonPorts.xml
sudo rm nmap_$1_tcpFullPorts.xml
sudo rm nmap_$1_aggressive.xml
