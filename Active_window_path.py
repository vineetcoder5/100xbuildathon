import time
import socket
import win32gui
import win32com.client

SERVER_ADDRESS = ('localhost', 65432)

def get_active_explorer_path():
    hwnd_active = win32gui.GetForegroundWindow()
    shell = win32com.client.Dispatch("Shell.Application")
    for window in shell.Windows():
        if window.HWND == hwnd_active:
            try:
                return window.Document.Folder.Self.Path
            except Exception:
                pass
    return None

if __name__ == "__main__":
    # Create a single UDP socket (SOCK_DGRAM) and reuse it
    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print("🟢 Explorer path monitor running (UDP, no TCP connect)...")

    try:
        while True:
            path = get_active_explorer_path()
            if path:
                print("Active Explorer Path:", path)
                udp_sock.sendto(path.encode('utf-8'), SERVER_ADDRESS)
            else:
                print("Active window is not an Explorer folder.")
                # Optionally send a blank message or skip:
                # udp_sock.sendto(b"", SERVER_ADDRESS)
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping monitor...")
    finally:
        udp_sock.close()
