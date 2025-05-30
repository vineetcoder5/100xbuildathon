import time
import win32gui
import win32com.client


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
    print("🟢 Explorer path monitor running (UDP, no TCP connect)...")

    try:
        while True:
            path = get_active_explorer_path()
            if path:
                print("Active Explorer Path:", path)
            else:
                print("Active window is not an Explorer folder.")
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping monitor...")
