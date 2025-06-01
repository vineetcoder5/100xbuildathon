from openai import OpenAI
import base64
import json
import os
import re

# --- User info setup ---
USER_INFO_FILE = "user_info.json"
CONVO_FILE = "conversation.json"

def save_user_info(data):
    with open(USER_INFO_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_user_info():
    if os.path.exists(USER_INFO_FILE):
        with open(USER_INFO_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                pass
    return {"Name": "Unknown", "Email": "unknown@example.com", "Role": "User", "Tokens": 0}

existing_data = load_user_info()

# --- Conversation history setup ---

def load_conversation():
    if os.path.exists(CONVO_FILE):
        with open(CONVO_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

def save_conversation(convo):
    with open(CONVO_FILE, "w", encoding="utf-8") as f:
        json.dump(convo, f, ensure_ascii=False, indent=2)

def clear_conversation():
    if os.path.exists(CONVO_FILE):
        os.remove(CONVO_FILE)

# --- Helpers to encode inputs ---

def encode_image(image_path):
    with open(image_path, 'rb') as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")
    

def encode_file(file_path):
    with open(file_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode("utf-8")


def is_image_file(filename):
    pattern = r"^(.+?)\.(jpg|jpeg|png|gif|bmp|webp|tiff|svg)$"
    return bool(re.match(pattern, filename, re.IGNORECASE))

# --- Main response function ---

def get_response(image1, image2, file_path, file_name, message,recent_path):
    # Check token balance
    present_token = int(existing_data.get("Tokens", 0))
    if present_token < 100:
        return "Not Enough tokens please buy from website"

    # Prepare input payload
    if file_path is None:
        base64_image1 = encode_image(image1)
        base64_image2 = encode_image(image2)
        inp = [
            { "type": "input_image", "image_url": f"data:image/jpeg;base64,{base64_image1}" },
            { "type": "input_image", "image_url": f"data:image/jpeg;base64,{base64_image2}" },
            { "type": "input_text",  "text": message }
        ]
    else:
        if is_image_file(file_name):
            base64_image1 = encode_image(image1)
            inp = [
                { "type": "input_image", "image_url": f"data:image/jpeg;base64,{base64_image1}" },
                { "type": "input_text",  "text": message }
            ]
        else:
            base64_file = encode_file(file_path)
            inp = [
                { "type": "input_file", "filename": file_name, "file_data": f"data:application/pdf;base64,{base64_file}" },
                { "type": "input_text", "text": message }
            ]

    # Load conversation history and append new user message
    conversation = load_conversation()
    conversation.append({"role": "user", "content": inp})

    # System prompt
    system_prompt = {
        "role": "system",
        "content": [
            # { "type": "input_text", "text": 
            #   "you are a personal assistant you will be given screenshot of the computer screen "
            #   "or if a person looking at a file then file will be given to you. you have to answer the question "
            #   "given by the user. keep answer short." }
                        { "type": "input_text", "text": f"""
you are a personal assistant. who use python if required to complete the goal provided by the user.

Two screenshot of the computer screen will always be provided when user ask a question. one screenshot is current and one is 1 sec back. if a file get uploaded with only 1 currented screenshot will be provided.

Answer the user's question bases on the screenshot and the file if uploaded. you can generate python script if required to reach to the goal that user want in query. the user may ask the question outside the context of the screen he is viewing. so respond naturally.

The python script provided by you will run automatically in background with out human intervention. so respond directly with the result not with suggestions or explanations.

The Most recent foalder opened by user is # {recent_path} # if the information is usefull to reach user goal use it otherwise neglect it.

Make sure if you are using file path in python code use // instead of  \\ in file path.

Don't correct any spelling in file path.

don't do mistake in python indent and write proper comment in python script.

keep the response short.

The response must follow this JSON format:

{{
  "answer": "<the answer to user query>",
  "python_code": "<Full Python script as a string, or an empty string if no code is needed>"
}}

##Example:-

user:- hi
#response Generated
{{
  "answer": "Hi how are you",
  "python_code": ""
}}

user:- can you open download foalder
#response Generated
{{
  "answer": "sure I am opening download foalder",
  "python_code": "import os\nimport subprocess\n\ndef open_downloads_folder():\n    downloads_path = os.path.join(os.path.expanduser('~'), 'Downloads')\n    if os.name == 'nt':  # For Windows\n        subprocess.run(['explorer', downloads_path])\n    elif os.name == 'posix':  # For macOS or Linux\n        subprocess.run(['open' if sys.platform == 'darwin' else 'xdg-open', downloads_path])\n\nopen_downloads_folder()"
}}

""" }
        ]
    }

    # Build full API input
    api_input = [system_prompt] + conversation

    # Call OpenAI API
    client = OpenAI(api_key="")
    response = client.responses.create(
        model="gpt-4.1-mini",
        input=api_input,
        text={"format": {"type": "text"}},
        reasoning={},
        tools=[
            {"type": "web_search_preview", "user_location": {"type": "approximate"}, "search_context_size": "medium"}
        ],
        temperature=1,
        max_output_tokens=20048,
        top_p=1,
        store=True
    )

    # Extract and save assistant response
    assistant_response = response.output_text
    # conversation.append({"role": "assistant", "content": assistant_response})
    # save_conversation(conversation)

    # Update token balance
    total_tokens = response.usage.total_tokens
    existing_data["Tokens"] = present_token - total_tokens
    save_user_info(existing_data)

    return assistant_response
