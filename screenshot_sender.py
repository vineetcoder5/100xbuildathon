import os
import threading
from datetime import datetime
import mss
from PIL import Image
import time

OUTPUT_DIR = "screenshots"
MAX_SCREENSHOTS = 5

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Start in running state
running_event = threading.Event()
running_event.set()  # Start taking screenshots immediately

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
    capture_screenshots()
