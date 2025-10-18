echo -e "\033[32mDetected web server, running hawkeye\033[0m"
sudo ../Hawkeye/hawkeye.py --target $1
echo -e "\033[32mFinished hawkeye scan\033[0m"
