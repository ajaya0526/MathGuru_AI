import os
import json
import socket
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# 📁 Local user DB path
USER_DB = os.path.join(os.path.dirname(__file__), 'users.json')

# 🧾 Create users.json if not present
if not os.path.exists(USER_DB):
    with open(USER_DB, 'w', encoding='utf-8') as f:
        json.dump({}, f)

# 🌐 Check if internet is available
def is_internet_available():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=2)
        return True
    except:
        return False

# 📂 Load users from file
def load_users():
    try:
        with open(USER_DB, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"[ERROR] Loading users: {e}")
        return {}

# 💾 Save users to file
def save_users(users):
    try:
        with open(USER_DB, 'w', encoding='utf-8') as f:
            json.dump(users, f, indent=4)
    except Exception as e:
        print(f"[ERROR] Saving users: {e}")

# ✅ Local login check
def check_login(username, password):
    users = load_users()
    if users.get(username) == password:
        if is_internet_available():
            give_gemini_feedback(f"A student just logged in with username {username}")
        return True
    return False

# ➕ Register user locally, use Gemini for feedback if online
def register_user(username, password):
    users = load_users()
    if username in users:
        if is_internet_available():
            give_gemini_feedback(f"Student tried to register with existing username '{username}'")
        return False
    users[username] = password
    save_users(users)
    if is_internet_available():
        give_gemini_feedback(f"New student registered with username '{username}'")
    return True

# 🔁 Reset password locally + notify Gemini if online
def reset_password(username, new_password):
    users = load_users()
    if username in users:
        users[username] = new_password
        save_users(users)
        if is_internet_available():
            give_gemini_feedback(f"Student '{username}' reset their password.")
        return True
    return False

# 🤖 Gemini feedback function (optional use case)
def give_gemini_feedback(prompt):
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        print("[Gemini Feedback]:", response.text.strip())
    except Exception as e:
        print("[GEMINI FEEDBACK ERROR]:", e)
