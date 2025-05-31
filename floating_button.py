import tkinter as tk
from PIL import Image, ImageTk, ImageDraw
import subprocess
import time
import socket
import sys

# ————— Networking & Chatbot launcher —————
chatbot_process = None
drag_threshold = 5
press_time = 0
click_pos = (0, 0)

def send_to_server(message):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(message.encode(), ('localhost', 65432))
    sock.close()

def open_chatbot():
    global chatbot_process
    if chatbot_process is None or chatbot_process.poll() is not None:
        send_to_server("CHATBOT: Floating icon clicked")
        chatbot_process = subprocess.Popen([sys.executable, "chatbot_window.py"])
        root.withdraw()

# ————— Drag / click handlers —————
def start_move(event):
    global press_time, click_pos
    press_time = time.time()
    click_pos = (event.x_root, event.y_root)
    root.x = event.x
    root.y = event.y

def do_move(event):
    dx = abs(event.x_root - click_pos[0])
    dy = abs(event.y_root - click_pos[1])
    if dx > drag_threshold or dy > drag_threshold:
        x = root.winfo_x() + event.x - root.x
        y = root.winfo_y() + event.y - root.y
        root.geometry(f"+{x}+{y}")

def on_release(event):
    dx = abs(event.x_root - click_pos[0])
    dy = abs(event.y_root - click_pos[1])
    held_time = time.time() - press_time
    if dx < drag_threshold and dy < drag_threshold and held_time < 0.4:
        open_chatbot()

# ————— Build transparent circular window (Windows) —————
root = tk.Tk()
root.title("Floating Circle")
root.geometry("80x80+50+50")
root.overrideredirect(True)
root.attributes("-topmost", True)

# Use a background color unlikely to appear in the image, then make it transparent
root.config(bg='pink')
root.wm_attributes('-transparentcolor', 'pink')

canvas = tk.Canvas(root, width=80, height=80, bg='pink', highlightthickness=0)
canvas.pack()

# Draw a smooth circular border
canvas.create_oval(2, 2, 78, 78, outline="#1E90FF", width=4)

# ————— Load & mask the octopus image —————
# Ensure you have an "octopus.png" (ideally square) in the same folder
raw = Image.open("octopus.jpeg").convert("RGBA").resize((70, 70), Image.LANCZOS)

# Create circular mask
mask = Image.new("L", (70, 70), 0)
draw = ImageDraw.Draw(mask)
draw.ellipse((0, 0, 70, 70), fill=255)

# Apply mask to image
raw.putalpha(mask)

# Convert to a PhotoImage
octo_img = ImageTk.PhotoImage(raw)

# Place image at center and capture its canvas item ID
image_id = canvas.create_image(40, 40, image=octo_img)

# ————— Bind events for drag & click —————
# Canvas-wide bindings
canvas.bind("<Button-1>", start_move)
canvas.bind("<B1-Motion>", do_move)
canvas.bind("<ButtonRelease-1>", on_release)

# Also bind directly on the octopus image
canvas.tag_bind(image_id, "<Button-1>", start_move)
canvas.tag_bind(image_id, "<B1-Motion>", do_move)
canvas.tag_bind(image_id, "<ButtonRelease-1>", on_release)

# ————— Monitor chatbot process to re-show button —————
def check_chatbot_closed():
    global chatbot_process
    if chatbot_process and chatbot_process.poll() is not None:
        root.deiconify()
        chatbot_process = None
    root.after(100, check_chatbot_closed)

check_chatbot_closed()
root.mainloop()
