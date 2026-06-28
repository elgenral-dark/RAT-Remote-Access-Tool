Advanced RAT Admin & Victim  
===========================

Project Overview
----------------
A lightweight, cross‑platform Remote Access Trojan (RAT) written in Python 3.10+.  
- **Admin** – central command and control server.  
- **Victim** – client that connects to the admin, executes commands, uploads files, takes screenshots, and lists processes.  
- Supports TLS, base64 file transfer, and a simple CLI for the admin.

Project Structure
-----------------
```
advanced-rat-admin-victim/
├── admin.py
├── victim.py
└── README.md
```

Prerequisites
-------------
- Python 3.10+  
- pip packages: `psutil`, `mss` (for screenshots)  
  ```bash
  pip install psutil mss
  ```

Configuration
-------------
- Edit `HOST` and `PORT` in both `admin.py` and `victim.py`.  
- `HOST` in `victim.py` must point to the admin’s IP.  
- `PORT` must match on both sides.  
- Optional: Change `BUFFER_SIZE`, `ENCODING`, or enable `ssl` parameters.

Running the Admin
-----------------
```bash
python3 admin.py
```
- The admin listens on all interfaces (`0.0.0.0`) at the configured port.  
- Connected victims appear in the CLI.  
- Use the numbered menu to select a victim and send commands.

Available Admin Commands
-----------------------
1. **Execute shell command** – type the command string.  
2. **Upload file** – specify local file path and destination path on victim.  
3. **Take screenshot** – captures the victim’s primary monitor.  
4. **List processes** – retrieves running process list from victim.  
5. **Download file** – victim can send a file; it’s saved locally.  
6. **Send custom JSON** – for advanced interactions.

Example Admin CLI Flow
----------------------
```
Connected victims:
  1. ('192.168.1.50', 52673)
Select victim number (or 'q' to quit): 1

Commands:
  1. Execute shell command
  2. Upload file
  3. Take screenshot
  4. List processes
  5. Download file
  6. Send custom JSON
Choose command: 1
Enter shell command: whoami
```

Running the Victim
------------------
```bash
python3 victim.py
```
- The victim connects to the admin, sends a status message, and waits for commands.  
- All communication is wrapped in TLS (self‑signed certs).  
- Screenshots, files, and process lists are transmitted as base64‑encoded JSON.

Extending the RAT
-----------------
- **Add new command types**: Extend `handle_command` in `victim.py` and `process_message` in `admin.py`.  
- **Persistence**: Add a startup hook to run victim on boot.  
- **Stealth**: Disable console window on Windows (`subprocess.Popen(..., creationflags=subprocess.CREATE_NO_WINDOW)`).

License
-------
MIT License – free to use, modify, and distribute.

Happy hacking!
