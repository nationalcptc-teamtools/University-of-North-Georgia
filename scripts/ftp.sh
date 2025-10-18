echo -e "\033[32mDetected FTP, attempting anonymous logon\033[0m"
wget -r ftp://$1
echo -e "\033[32mFinished ftp anonymous logon attempt\033[0m"
