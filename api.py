
import os
from typing import List
from openai_test import get_response

def get_recent_screenshots(directory: str, count: int = 2) -> List[str]:
    """
    Return the file paths of the `count` most recent .png files
    in `directory`, sorted newest first.
    """
    # List all PNGs in the directory
    files = [
        os.path.join(directory, fn)
        for fn in os.listdir(directory)
        if fn.lower().endswith('.png')
    ]
    # Sort by modification time, descending
    files.sort(key=lambda p: os.path.getmtime(p), reverse=True)
    # Return up to `count` items
    return files[:count]


# # ── Example Usage ──
# if __name__ == "__main__":
#     screenshot_dir = "screenshots"
#     recent_two = get_recent_screenshots(screenshot_dir, 2)
#     print("Most recent screenshots:")
#     for path in recent_two:
#         print("  ", path)

def response(message,recent_path = None,file_name = None,file_path = None):
    screenshot_dir = "screenshots"
    recent_two = get_recent_screenshots(screenshot_dir, 2)
    if (file_name==None or file_path == None):
        return get_response(recent_two[0],recent_two[1],None,None,message,recent_path)
    else:
        return get_response(recent_two[0],recent_two[1],file_path,file_name,message,recent_path)



