# main_server.py
from api import response
import socket
import re
import os
from collections import deque
import time
from extract_json import extract_and_execute
import json
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

def update_message(Current_message):
    HISTORY_FILE = "chat_history.json"
    message_history = []
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            try:
                old_history = json.load(f)
                for sender, msg in old_history:
                    message_history.append((sender, msg))
            except json.JSONDecodeError:
                pass 
    Current_message = Current_message.decode().strip()
    message_history.append(("server", Current_message))
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(message_history, f, ensure_ascii=False, indent=2)       

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
            # print("click")
            # print(message)
            # continue
            ans = search_file()
            # print(recent_path)
            if ans == "Not Found" or ans == "Google Chrome":
                print("image")
                resul = response(message,recent_path)
            else: 
                print("file")
                # print(ans)
                recent_path = ans[1]
                resul = response(message,recent_path,ans[0],ans[1])
            resull = resul.encode("utf-8")
            try:
                server_socket.sendto(resull, ('localhost', 65436))
            except:
                print("error")
                update_message(resull)
            resul = extract_and_execute(resul)
            resul = resul.encode("utf-8")
            server_socket.sendto(resul, ('localhost', 65436))
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
    while True:
        try:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            start_server()
        except ConnectionResetError:
            print("Client forcibly closed the connection. Continuing...")
        except Exception as e:
            print("Client forcibly closed the connection. Continuing...")
        
