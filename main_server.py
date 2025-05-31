# main_server.py
import socket
import re
import os
from collections import deque
import time
# Dictionary to store file info

recent_path = None
file_open_log = {}
last_5_files = deque(maxlen=5)
def notify_monitors():
    msg = "REQUEST:STATE_CHECK"
    for port in [65433, 65434,65437]:  # 65434 for active window, 65433 for file launcher
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.sendto(msg.encode(), ('localhost', port))
            sock.close()
        except Exception as e:
            print(f"❌ Failed to notify port {port}: {e}")

def extract_file_info(message):
    # Extract all quoted strings
    quoted_strings = re.findall(r'"(.*?)"', message)
    path = quoted_strings[-1]
    # Check if it's a valid file path with an extension
    # print(path)
    if os.path.splitext(path)[1]:  # Has a file extension
        file_name = os.path.basename(path)
        file_open_log[file_name] = path
        print(f"📁 Extracted File -> Name: {file_name}, Path: {path}")
     # Only extract first valid file
    # else: skip e.g., program executables like wps.exe
def file_name(message):
    # 1) Chrome special-case
    if "Google Chrome" in message:
        file = "Google Chrome"
    else:
        # 2) remove prefix
        content = message.partition("WINDOW:")[2].strip()
        # 3) try to match the first filename (with extension)
        m = re.search(r'([\w\s\-.]+\.[A-Za-z0-9]{1,10})', content)
        if m:
            file = m.group(1).strip()
        else:
            # fallback: up to first double-space or last " - "
            if "  " in content:
                file = content.split("  ", 1)[0].strip()
            else:
                file = content.rsplit(" - ", 1)[0].strip()
    # 4) record & return
    if file:
        last_5_files.append(file)
    return file

def search_file():
    for i in reversed(last_5_files):
        if i == "Floating Circle":
            continue
        elif i=="Google Chrome":
            return "Google Chrome"
        elif i in file_open_log:
            if os.path.exists(file_open_log[i]):
                return [i,file_open_log[i]]
            else:
                return "Not Found"
        else:
            print(i)
            return "Not Found"
    return "Not Found"

        

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
def chatbot_clicked():
    global recent_path
    print("🤖 Chatbot clicked — performing exclusive action...")
    print(file_open_log)
    print(last_5_files)
    print(recent_path)
    while True:
        data, _ = server_socket.recvfrom(1024)
        message = data.decode()
        # print(message)
        if message.startswith("Path:") or message.startswith("REQUEST:") or message.startswith("WINDOW:") or message.startswith("LAUNCH:") or message.startswith("SCREENSHOT:"): 
            continue
        elif message == "CHATBOT: Chatbot closed":
            break
        elif message:
            #here the logic og llm call will go
            server_socket.sendto("llm response", ('localhost', 65436))

    print("done")
    notify_monitors()
    # time.sleep(5)

def start_server():
    global recent_path
    # server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind(('localhost', 65432))

    print("📋 Server listening for messages...\n")
    
    while True:
        data, _ = server_socket.recvfrom(1024)
        message = data.decode()
        if message == "CHATBOT: Floating icon clicked":
            notify_monitors()
            print(f"[From Chatbot] {message[8:].strip()}") 
            chatbot_clicked()
            continue
        elif message.startswith("WINDOW:"):
            print(file_name(message))
            # print(f"[From Window Monitor] {message[7:].strip()}")
        elif message.startswith("LAUNCH:"):
            # print(f"[From File Launcher] {message[7:].strip()}")
            extract_file_info(message)
        elif message.startswith("SCREENSHOT:"):
            path = message[11:].strip().strip('"')
            print(f"🖼️ Screenshot received from sender: {path}")
        elif message.startswith("Path:"):
            path = message[5:].strip().strip('"')
            recent_path = path
            print(f"Foalder Path: {path}")
        else:
            print(f"[Unknown Source] {message.strip()}")

if __name__ == "__main__":
    start_server()
