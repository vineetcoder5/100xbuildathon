import os
import psutil
import wmi
import threading
import time

# Global cache and lock for thread-safe PID access
explorer_pids = set()
pid_lock = threading.Lock()

def get_explorer_pids():
    return {p.pid for p in psutil.process_iter(['name']) if p.info['name'] == 'explorer.exe'}

def refresh_explorer_pids(interval, stop_event):
    while not stop_event.is_set():
        with pid_lock:
            explorer_pids.clear()
            explorer_pids.update(get_explorer_pids())
        time.sleep(interval)

def monitor_file_launches():
    c = wmi.WMI(moniker="//./root/cimv2")
    watcher = c.ExecNotificationQuery(
        "SELECT * FROM __InstanceCreationEvent WITHIN 0.1 WHERE TargetInstance ISA 'Win32_Process'"
    )

    stop_event = threading.Event()
    pid_refresh_thread = threading.Thread(target=refresh_explorer_pids, args=(2, stop_event))
    pid_refresh_thread.daemon = True
    pid_refresh_thread.start()

    print("🟢 File Launcher Monitor running (without sending messages)...")

    try:
        while True:
            event = watcher.NextEvent()
            new_proc = event.TargetInstance
            cmdline = new_proc.CommandLine or ""
            parent = new_proc.ParentProcessId

            with pid_lock:
                if parent in explorer_pids:
                    if '\"' in cmdline or os.path.exists(cmdline.split()[0]):
                        print(f"LAUNCH DETECTED: {cmdline}")

    except KeyboardInterrupt:
        stop_event.set()
        pid_refresh_thread.join()

if __name__ == "__main__":
    monitor_file_launches()
