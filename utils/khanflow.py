import os
import socket
import google.generativeai as genai
from dotenv import load_dotenv

# 🔐 Load and configure Gemini API
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# 🤖 Use fast and cheap Gemini model
try:
    model = genai.GenerativeModel("gemini-2.0-flash")
except Exception as e:
    print("[Model Init Error]:", e)

# 🌐 Check if internet is available
def is_internet_available():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=2)
        return True
    except:
        return False

# 💡 Offline fallback hints by topic
def get_offline_hint(problem, step):
    q = problem.lower()
    if step < 5:
        if "add" in q or "+" in q:
            return "🔍 Try lining up digits by place value and start adding from the right."
        elif "subtract" in q or "-" in q:
            return "🔍 Subtract from right to left. Borrow if needed!"
        elif "multiply" in q or "*" in q or "times" in q:
            return "🔍 Try breaking one number into smaller parts. Distribute and multiply."
        elif "divide" in q or "/" in q:
            return "🔍 Think how many times the divisor fits into the dividend."
        elif "^" in q or "square" in q:
            return "🔍 Remember: squaring a number means multiplying it by itself."
        else:
            return "🔍 Identify the operation. Start with what you understand first."
    else:
        return "✅ Final Answer: Please try solving manually. No internet to fetch final solution."

# 🎯 Main function (online/offline auto)
def get_khan_hint(problem, step=1, grade="4"):
    if is_internet_available():
        try:
            prompt = f"""
You are a friendly math tutor teaching a Grade {grade} student.

The student is solving: "{problem}"

Your goal is to teach the student in exactly 5 steps.

Rules:
- If step < 5 → Give only ONE short, clear HINT that gently guides (not solves).
- If step == 5 → Give the FINAL ANSWER with explanation. Begin with "✅ Final Answer:"

DO NOT:
- Solve the full problem before step 5.
- Mention "Hint 1" or "Step X" anywhere in the text.
- Repeat previous hints or explain everything again.

Use only:
- 🔍 Hint for steps 1–4 (no solving).
- ✅ Final Answer for step 5 (solve and explain cleanly).

Now provide the correct response based on step {step}.
"""
            response = model.generate_content(prompt.strip())
            return response.text.strip()
        except Exception as e:
            print(f"[KHANFLOW ONLINE ERROR]: {e}")
            return f"💡 Hint {step}: ❌ Gemini error occurred. Try again."
    else:
        return get_offline_hint(problem, step)
