
## TEAM-X network access

After a successful setup or verification, the setup script can ask for the IPv4 address teammates should use to reach the PwnDoc host. You do not need to know this address ahead of time.

Interactive use:

```bash
python3 setup_cptc_findings_pwndoc.py --template ./CPTC_PwnDoc_Findings_Only_v2.docx
```

At the end, enter the LAN/competition-network IPv4 address assigned to the PwnDoc host. The script prints the TEAM-X URL in the form:

```text
https://HOST_IP:8443
```

You can also supply the address directly:

```bash
python3 setup_cptc_findings_pwndoc.py \
  --template ./CPTC_PwnDoc_Findings_Only_v2.docx \
  --team-ip 192.168.1.42
```

The script checks the current port 8443 listener and warns if PwnDoc appears to be bound only to localhost. The entered address is the address teammates use to connect; PwnDoc/Docker should normally publish port 8443 on all host interfaces (`0.0.0.0:8443`).

If the PwnDoc host is a VM, use a network mode that permits teammates to reach the VM directly (typically bridged networking when allowed by the competition network/rules).
