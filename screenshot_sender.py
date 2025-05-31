import os
import socket
import threading
from datetime import datetime
import mss
from PIL import Image
import time

SERVER_ADDRESS = ('localhost', 65432)
LISTEN_PORT = 65437  # Port to listen for toggle messages
OUTPUT_DIR = "screenshots"
MAX_SCREENSHOTS = 5

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Start in running state
running_event = threading.Event()
running_event.set()  # Start taking screenshots immediately

def send_to_server(message):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.sendto(message.encode(), SERVER_ADDRESS)

# 🔊 Listen for toggle commands from the server
def listen_from_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('localhost', LISTEN_PORT))
    print("📡 Listening for server toggle messages...")

    while True:
        data, _ = sock.recvfrom(1024)
        message = data.decode().strip()
        print("📩 Received toggle from server:", message)

        # Toggle running state
        if running_event.is_set():
            running_event.clear()
            print("⏸️ Paused screenshotting.")
        else:
            running_event.set()
            print("▶️ Resumed screenshotting.")

# 📸 Screenshot capturing
def capture_screenshots():
    with mss.mss() as sct:
        print("📸 Screenshot system started.")
        try:
            while True:
                if running_event.is_set():
                    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                    filepath = os.path.join(OUTPUT_DIR, f"screenshot_{timestamp}.png")

                    img = sct.grab(sct.monitors[1])
                    Image.frombytes("RGB", img.size, img.rgb).save(filepath)
                    print(f"🖼️ Captured: {filepath}")
                    send_to_server(f'SCREENSHOT: "{filepath}"')

                    # Cleanup old screenshots
                    files = sorted(
                        [os.path.join(OUTPUT_DIR, f) for f in os.listdir(OUTPUT_DIR) if f.endswith(".png")],
                        key=os.path.getmtime
                    )
                    if len(files) > MAX_SCREENSHOTS:
                        for old_file in files[:-MAX_SCREENSHOTS]:
                            os.remove(old_file)
                            print(f"🗑️ Deleted: {old_file}")

                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Screenshot capture stopped.")

if __name__ == "__main__":
    threading.Thread(target=listen_from_server, daemon=True).start()
    capture_screenshots()
