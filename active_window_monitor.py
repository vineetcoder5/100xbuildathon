import socket
import time
import win32gui
import select
import re

SERVER_ADDRESS = ('localhost', 65432)
def get_active_window_title():
    window = win32gui.GetForegroundWindow()
    return win32gui.GetWindowText(window)
def run_monitor():
    send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    last_send_time = 0

    print("🟢 Active Window Monitor running...")

    while True:
        # Send active window title every 2 seconds
        current_time = time.time()
        if current_time - last_send_time >= 0.5:
            title = get_active_window_title()
            message = f"WINDOW: {title}"
            send_socket.sendto(message.encode(), SERVER_ADDRESS)
            last_send_time = current_time
            print(message)


if __name__ == "__main__":
    run_monitor()
