#!/bin/bash
echo -e "\033[32mStarting nmap aggressive port scan on $1\033[0m"
nmap --stats-every 5s -p$2 -A $1 -oN upload/nmap_$1_aggressive.txt -oX nmap_$1_aggressive.xml
sudo chmod 666 upload/nmap_$1_aggressive.txt
sudo chmod 666 nmap_$1_aggressive.xml
echo -e "\033[32mFinished nmap aggressive port scan on $1\033[0m"
echo -e "\033[32mStarting udp common port scan on $1\033[0m"
sudo nmap --stats-every 5s -sU $1 -oN upload/nmap_$1_udpCommonPorts.txt -oX nmap_$1_udpCommonPorts.xml
sudo chmod 666 upload/nmap_$1_udpCommonPorts.txt
sudo chmod 666 nmap_$1_udpCommonPorts.xml
echo -e "\033[32mFinished udp common port scan on $1\033[0m"
