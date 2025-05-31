import tkinter as tk
from tkinter import ttk
import socket
import threading
import json
import os
import tempfile, base64, zlib

# — Network configuration —
SERVER_ADDRESS = ('localhost', 65432)
CLIENT_PORT = 65436  # port this client listens on

# — Load icon —
ICON = zlib.decompress(base64.b64decode(
    'eJxjYGAEQgEBBiDJwZDBy' 'sAgxsDAoAHEQCEGBQaIOAg4sDIgACMUj4JRMApGwQgF/ykEAFXxQRc='
))
_, ICON_PATH = tempfile.mkstemp()
with open(ICON_PATH, 'wb') as icon_file:
    icon_file.write(ICON)

# — Message history storage —
HISTORY_FILE = "chat_history.json"
message_history = []  # list of tuples: ("user"|"server", "message")

# — User info file —
USER_INFO_FILE = "user_info.json"

# 🔹 Send a UDP message to the main server
def send_to_server(message):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(message.encode(), SERVER_ADDRESS)
    finally:
        sock.close()

# 🔹 Listen for server messages and display them
def listen_to_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('localhost', CLIENT_PORT))
    while True:
        data, _ = sock.recvfrom(4096)
        msg = data.decode().strip()
        message_history.append(("server", msg))
        display_message(msg, sender="server")

# 🔹 Persist chat history on close and notify server
def on_close():
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(message_history, f, ensure_ascii=False, indent=2)
    send_to_server("CHATBOT: Chatbot closed")
    root.destroy()

# 🔹 Notify server on minimize, then close
def on_minimize(event):
    if root.state() == 'iconic':  # only on real minimize
        on_close()

# 🔹 Display a message bubble in the chat area
def display_message(text, sender="user"):
    bg_color = "#d1ffd6" if sender == "user" else "#ffffff"
    if sender == "user":
        pad, anchor = (50, 10), "e"
    else:
        pad, anchor = (10, 50), "w"

    bubble = tk.Frame(scrollable_frame, bg="#f4f4f8")
    lbl = tk.Label(
        bubble,
        text=text,
        bg=bg_color,
        wraplength=300,
        font=("Arial", 11),
        justify="left",
        padx=10,
        pady=5
    )
    lbl.pack()
    bubble.pack(anchor=anchor, pady=4, padx=pad)

    canvas.update_idletasks()
    canvas.yview_moveto(1)

# 🔹 Send user message when Send button clicked or Enter pressed
def on_send():
    msg = user_input.get().strip()
    if not msg:
        return
    message_history.append(("user", msg))
    display_message(msg, sender="user")
    send_to_server(f"CHATBOT: {msg}")
    user_input.delete(0, tk.END)

# — Load/save user info —
def load_user_info():
    if os.path.exists(USER_INFO_FILE):
        with open(USER_INFO_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                pass
    # default
    return {"Name": "Unknown", "Email": "unknown@example.com", "Role": "User"}

def save_user_info(data):
    with open(USER_INFO_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# — Populate overlay with view/edit mode —
def populate_user_info(edit_mode=False):
    # Change header title
    header_label.config(text="User Info")
    # Raise overlay
    user_info_frame.lift()

    # Clear old widgets
    for w in user_info_frame.winfo_children():
        w.destroy()

    data = load_user_info()
    tk.Label(user_info_frame,
             text="User Info",
             font=("Arial", 16, "bold"),
             bg="#f4f4f8").pack(pady=10)

    entries = {}
    for key, val in data.items():
        row = tk.Frame(user_info_frame, bg="#f4f4f8")
        row.pack(fill="x", padx=20, pady=10)
        tk.Label(row,
                 text=f"{key}:",
                 font=("Arial", 12),
                 bg="#f4f4f8",
                 width=15,
                 anchor="w").pack(side="left")
        # print(key)
        if edit_mode and key=="KEY":
            e = tk.Entry(row, font=("Arial", 12), width=30)
            e.insert(0, str(val))
            e.pack(side="left", padx=5)
            entries[key] = e
        else:
            tk.Label(row,
                     text=str(val),
                     font=("Arial", 12),
                     bg="#f4f4f8").pack(side="left")

    btns = tk.Frame(user_info_frame, bg="#f4f4f8")
    btns.pack(pady=20)

    # Back button
    tk.Button(btns,
              text="← Back to Chat",
              font=("Arial", 12),
              command=back_to_chat).pack(side="left", padx=5)

    # Edit or Save
    if edit_mode:
        tk.Button(btns,
                  text="💾 Save",
                  font=("Arial", 12),
                  bg="#4CAF50",
                  fg="white",
                  command=lambda: save_and_back(entries)
                  ).pack(side="left", padx=5)
    else:
        tk.Button(btns,
                  text="✏️ Edit",
                  font=("Arial", 12),
                  bg="#2196F3",
                  fg="white",
                  command=lambda: populate_user_info(edit_mode=True)
                  ).pack(side="left", padx=5)

def save_and_back(entries):
    existing_data = load_user_info()
    for k, e in entries.items():
        existing_data[k] = e.get().strip()
    save_user_info(existing_data)
    populate_user_info(edit_mode=False)

def back_to_chat():
    # Restore header and hide overlay
    header_label.config(text="OCTOPUS")
    user_info_frame.lower()
    # Ensure chat and input are on top
    chat_frame.lift()
    input_frame.lift()
def check_focus():
    if root.focus_displayof() is None:
        on_close()
    else:
        root.after(500, check_focus) 
# — Build the UI —
root = tk.Tk()
root.title("OCTOPUS")
root.iconbitmap(default=ICON_PATH)
root.geometry("400x550")
root.configure(bg="#f4f4f8")
root.resizable(False, False)

# Close/minimize bindings
root.protocol("WM_DELETE_WINDOW", on_close)
# root.bind("<Unmap>", on_close)
root.after(1000, check_focus)


# Header
header = tk.Frame(root, bg="#a259ff", height=60)
header.pack(fill=tk.X)
header_label = tk.Label(
    header,
    text="OCTOPUSS-AI",
    fg="white",
    bg="#a259ff",
    font=("Arial", 14, "bold")
)
header_label.pack(side="left", padx=10, pady=15)

# User Info button
tk.Button(
    header,
    text="👤 User Info",
    font=("Arial", 10, "bold"),
    bg="#a259ff",
    fg="white",
    bd=0,
    cursor="hand2",
    command=lambda: populate_user_info(False)
).place(relx=1.0, x=-10, y=15, anchor="ne")

# Chat display area
chat_frame = tk.Frame(root, bg="#f4f4f8")
chat_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

canvas = tk.Canvas(chat_frame, bg="#f4f4f8", highlightthickness=0)
scrollbar = ttk.Scrollbar(chat_frame, orient="vertical", command=canvas.yview)
scrollable_frame = tk.Frame(canvas, bg="#f4f4f8")
scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)

canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)
canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# Mouse wheel scrolling
canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
canvas.bind_all("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))
canvas.bind_all("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))

# Input area
input_frame = tk.Frame(root, bg="#ffffff", bd=1, relief=tk.SUNKEN)
input_frame.pack(fill=tk.X, padx=10, pady=8)

user_input = tk.Entry(input_frame, font=("Arial", 12), relief=tk.FLAT)
user_input.pack(side="left", fill=tk.X, expand=True, padx=5, pady=5)
user_input.bind('<Return>', lambda event: on_send())

send_button = tk.Button(
    input_frame,
    text="Send",
    bg="#a259ff",
    fg="white",
    relief=tk.FLAT,
    command=on_send
)
send_button.pack(side="right", padx=5, pady=5)

# Load and display previous history
if os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        try:
            old_history = json.load(f)
            for sender, msg in old_history:
                message_history.append((sender, msg))
                display_message(msg, sender=sender)
        except json.JSONDecodeError:
            pass

# Overlay frame for user info (hidden by default)
user_info_frame = tk.Frame(root, bg="#f4f4f8")
user_info_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
user_info_frame.lower()  # hide underneath

# Start listening thread
threading.Thread(target=listen_to_server, daemon=True).start()

# Run the GUI
root.mainloop()
