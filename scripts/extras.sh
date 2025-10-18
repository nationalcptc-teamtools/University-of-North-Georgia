echo -e "\033[32mDetected Windows OS, running enum4linux-ng\033[0m"
enum4linux-ng $1 -oY upload/e4l_$1_defaultScan
sudo chmod 666 upload/e4l_$1_defaultScan.yaml
echo -e "\033[32mFinished enum4linux-ng\033[0m"
