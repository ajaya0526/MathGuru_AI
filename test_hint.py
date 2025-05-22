import google.generativeai as genai
import os

# Step 1: Configure API key
genai.configure(api_key=os.getenv("GEMINI_API_KEY", "AIzaSyBB_wjbbNfiGLNPKzaSUo-7Ou-Rf7YU4ZU"))

# Step 2: Create model
try:
    model = genai.GenerativeModel("gemini-2.0-flash")

    prompt = """
You are a friendly math tutor helping a Grade 4 student.

Question: What is 12 + 5 × 3?

Give Hint 1 only (DO NOT give the answer). Just guide them.
"""

    # Step 3: Call the API
    response = model.generate_content(prompt)

    print("\n✅ API CALL SUCCESSFUL!\n")
    print("🔍 RAW RESPONSE:\n", response)
    print("\n📘 HINT OUTPUT:\n", response.text.strip())

except Exception as e:
    print("\n❌ GEMINI API ERROR:")
    print(e)
