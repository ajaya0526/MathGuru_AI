hint_cache = {}
final_answer_cache = {}
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from utils.history import load_history, save_history  
import os
from werkzeug.utils import secure_filename
import re

from utils.ocr import extract_text
from utils.hints import get_next_hint, get_final_solution, reset_conversation
from utils.tts import synthesize_english_audio, synthesize_hindi_audio
from utils.feedback import evaluate_and_speak, save_feedback
from utils.auth import check_login, register_user, reset_password
from utils.khanflow import get_khan_hint
from utils.history import save_history, load_history

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['AUDIO_FOLDER'] = 'static/audio'
app.secret_key = 'mathguru-secret-key'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['AUDIO_FOLDER'], exist_ok=True)

# --- AUTH ROUTES --- #
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if check_login(username, password):
            session['user'] = username
            return redirect('/')
        return render_template('login.html', error="Invalid credentials.")
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if register_user(username, password):
            return redirect('/login')
        return render_template('register.html', error="User already exists.")
    return render_template('register.html')

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        username = request.form.get('username')
        new_password = request.form.get('new_password')
        if reset_password(username, new_password):
            return render_template('login.html', message="✅ Password reset successfully.")
        return render_template('forgot_password.html', error="⚠️ User not found.")
    return render_template('forgot_password.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')

# --- MAIN ROUTES --- #
@app.route('/')
def index():
    if 'user' not in session:
        return redirect('/login')
    return render_template('index.html')

@app.route('/manual-page')
def manual_page():
    if 'user' not in session:
        return redirect('/login')
    return render_template('manual.html')

@app.route('/feedback')
def feedback():
    if 'user' not in session:
        return redirect('/login')
    return render_template('feedback.html')

@app.route('/submit-feedback', methods=['POST'])
def submit_feedback():
    try:
        name = request.form.get('name', 'Anonymous')
        message = request.form.get('message', '')
        rating = request.form.get('rating', '5')
        save_feedback(name, message, rating)
        return "<h2>✅ Thank you for your feedback!</h2><a href='/'>💙 Back to Home</a>"
    except Exception as e:
        print(f"[FEEDBACK ERROR]: {e}")
        return "<h2>❌ Failed to save feedback</h2>", 500

@app.route('/manual', methods=['POST'])
def manual_input():
    if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    try:
        data = request.get_json()
        expression = data.get('expression', '').strip()
        
        # Save to session
        session["problem"] = expression
        session["step"] = 1
        session["grade"] = "5"

        # Get first hint
        hint = get_next_hint(expression)

        # Save history (manual input)
        save_history(expression, "", hint)

        return jsonify({
            'extracted': expression,
            'hint': hint
        })
    except Exception as e:
        print(f"[MANUAL ERROR]: {e}")
        return jsonify({'error': 'Manual input failed.'}), 500



@app.route('/scan_image', methods=['POST'])
def scan_image():
    if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        file = request.files.get('file')
        if not file:
            return jsonify({'error': '❌ No image received.'}), 400

        filename = secure_filename(file.filename)
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(image_path)

        extracted = extract_text(image_path)
        if not extracted or "no valid" in extracted.lower():
            return jsonify({'error': '❌ No valid math expression found.'})

        session["problem"] = extracted
        session["step"] = 1
        session["grade"] = "5"

        hint = get_next_hint(extracted)
        result = get_final_solution(extracted)

        audio_en = synthesize_english_audio(result["answer"])
        audio_hi = synthesize_hindi_audio(result["answer"])

        # Save history (image scan)
        save_history(extracted, result["answer"], hint)

        return jsonify({
            "extracted": extracted,
            "hint": hint,
            "result": result["answer"],
            "explanation": result["explanation"],
            "audio_en": audio_en,
            "audio_hi": audio_hi
        })

    except Exception as e:
        print(f"[SCAN_IMAGE ERROR]: {e}")
        return jsonify({'error': f"❌ Server error: {e}"})


@app.route('/upload', methods=['POST'])
def upload_camera_image():
    if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    file = request.files.get('image')
    if not file:
        return jsonify({'error': 'No image received'}), 400

    try:
        # Save the uploaded image
        filename = secure_filename(file.filename)
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(image_path)

        # Extract math text from image
        extracted = extract_text(image_path)
        if not extracted or "no valid" in extracted.lower():
            return jsonify({'error': '❌ No valid math expression found. Please try again with a clearer image.'}), 200

        # Save to session for hint tracking
        session["problem"] = extracted
        session["step"] = 1
        session["grade"] = "5"

        # ✅ Auto-generate Hint 1
        hint1 = get_khan_hint(extracted, 1, "5")
        audio_en = synthesize_english_audio(hint1)
        audio_hi = synthesize_hindi_audio(hint1)

        # Evaluate answer for result and steps
        result, audio_path = evaluate_and_speak(extracted)
        save_history(extracted, result["answer"], result["steps"])

        return jsonify({
            'extracted': extracted,
            'result': result["answer"],
            'steps': result["steps"],
            'audio': audio_path,
            'hint': hint1,
            'audio_en': audio_en,
            'audio_hi': audio_hi
        })

    except Exception as e:
        print(f"[UPLOAD ERROR]: {e}")
        return jsonify({'error': 'Image processing failed'}), 500



@app.route('/next_hint', methods=['POST'])
def next_hint():
    try:
        data = request.get_json()
        prompt = data.get("prompt", "").strip()
        hint = get_next_hint(prompt)
        return jsonify({ "hint": hint })
    except Exception as e:
        print(f"[NEXT HINT ERROR]: {e}")
        return jsonify({ "hint": "❌ Error generating hint." })




@app.route('/final_answer', methods=['POST'])
def final_answer():
    try:
        data = request.get_json()
        question = data.get("prompt", "").strip()
        result = get_final_solution(question)

        answer = result.get("answer", "❌ No answer provided.")
        explanation = result.get("explanation", "❌ No explanation available.")

        audio_en = synthesize_english_audio(explanation)
        audio_hi = synthesize_hindi_audio(explanation)

        # ⚠️ Optional: Only add if not already logged earlier
        save_history(question, answer, "")

        return jsonify({
            "answer": answer,
            "explanation": explanation,
            "audio_en": audio_en,
            "audio_hi": audio_hi
        })
    except Exception as e:
        print(f"[FINAL ANSWER ERROR]: {e}")
        return jsonify({
            "answer": "Error",
            "explanation": f"❌ Could not generate final answer: {str(e)}"
        })






@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if 'user' not in session:
        return redirect('/login')

    if request.method == 'POST':
        from utils.tts import synthesize_english_audio, synthesize_hindi_audio
        import re
        import google.generativeai as genai

        data = request.get_json()
        user_input = data.get("message", "").strip().lower()
        lang = data.get("lang", "en")

        if not user_input:
            return jsonify({"reply": "❗Please enter a question.", "audio_en": "", "audio_hi": ""})

        print("[DEBUG] User said:", user_input)

        # ✅ Case 1: App-related help
        app_keywords = ["app", "not working", "error", "bug", "problem in app"]
        if any(word in user_input for word in app_keywords):
            reply = "🛠️ If you're facing problems with the app, try restarting it or checking your internet connection. If issues persist, contact your teacher or technical support."
            audio_en = synthesize_english_audio(reply)
            audio_hi = synthesize_hindi_audio(reply)
            return jsonify({"reply": reply, "audio_en": audio_en, "audio_hi": audio_hi})

        # ✅ Case 2: Math confusion help
        math_keywords = ["i don't understand", "help me solve", "confused", "stuck", "math help"]
        if any(word in user_input for word in math_keywords):
            reply = "💡 Try breaking the math problem into smaller steps. Start with known formulas or use examples. You can also ask me to solve it step by step!"
            audio_en = synthesize_english_audio(reply)
            audio_hi = synthesize_hindi_audio(reply)
            return jsonify({"reply": reply, "audio_en": audio_en, "audio_hi": audio_hi})

        # ✅ Case 3: Small talk support
        if "can you help" in user_input or "who are you" in user_input:
            reply = "🤖 I'm MathGuru AI, your personal math tutor. I can explain concepts, solve problems, and help you learn better!"
            audio_en = synthesize_english_audio(reply)
            audio_hi = synthesize_hindi_audio(reply)
            return jsonify({"reply": reply, "audio_en": audio_en, "audio_hi": audio_hi})

        # ✅ Case 4: Simple math eval
        try:
            if re.fullmatch(r"[0-9+\-*/(). ]+", user_input):
                answer = str(eval(user_input))
                reply = f"The answer is {answer}"
                audio_en = synthesize_english_audio(reply)
                audio_hi = synthesize_hindi_audio(reply)
                return jsonify({"reply": reply, "audio_en": audio_en, "audio_hi": audio_hi})
        except Exception as e:
            print("[EVAL ERROR]:", e)

        # ✅ Case 5: Use Gemini for complex questions
        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(user_input)
            reply = response.text.strip()
            print("[DEBUG] Gemini says:", reply)
        except Exception as e:
            print("[GEMINI ERROR]:", e)
            reply = "🤖 Sorry, I couldn’t connect to the AI server."

        audio_en = synthesize_english_audio(reply)
        audio_hi = synthesize_hindi_audio(reply)

        return jsonify({"reply": reply, "audio_en": audio_en, "audio_hi": audio_hi})

    return render_template("chat.html")




@app.route('/hints')
def show_hint_page():
    if 'user' not in session:
        return redirect('/login')
    return render_template('hints.html', hint="Type a question to get your hint.", step=0, problem=None)

@app.route('/start-hint', methods=['POST'])
def start_hint():
    if 'user' not in session:
        return redirect('/login')
    problem = request.form.get("problem")
    grade = request.form.get("grade", "4")
    session["problem"] = problem
    session["step"] = 1
    session["grade"] = grade
    hint = get_khan_hint(problem, 1, grade)
    return render_template("hints.html", hint=hint, step=1, problem=problem)

@app.route('/next-hint-legacy', methods=['POST'])
def next_hint_legacy():
    if 'user' not in session:
        return redirect('/login')
    session["step"] += 1
    problem = session.get("problem")
    step = session["step"]
    grade = session.get("grade", "4")
    if step >= 5:
        final_text = get_khan_hint(problem, step, grade)
        if final_text.lower().startswith("hint 1:"):
            final_text = final_text.split(":", 1)[1].strip()
        try:
            english_audio = synthesize_english_audio(final_text)
            hindi_audio = synthesize_hindi_audio(final_text)
        except Exception as e:
            print("[AUDIO GENERATION ERROR]:", e)
            english_audio = ""
            hindi_audio = ""
        return jsonify({
            "hint": f"✅ Final Answer: {final_text}",
            "step": step,
            "audio": english_audio,
            "hindi_audio": hindi_audio
        })
    hint = get_khan_hint(problem, step, grade)
    return jsonify({"hint": f"💡 Hint {step}: {hint}", "step": step})

@app.route('/clear_history', methods=['POST'])
def clear_history():
    try:
        history_file = os.path.join(os.path.dirname(__file__), 'utils', 'history.json')
        if os.path.exists(history_file):
            with open(history_file, 'w', encoding='utf-8') as f:
                f.write("[]")  # Clear the history by writing an empty list
    except Exception as e:
        print("[Clear History Error]:", e)
    return redirect(url_for('history'))


@app.route('/history')
def history():
    logs = load_history()
    return render_template("history.html", logs=logs)

@app.route('/hint_audio', methods=['POST'])
def hint_audio():
    try:
        data = request.get_json()
        hint = data.get("hint", "").strip()
        print(f"[DEBUG] Generating audio for hint: {hint}")

        audio_en = synthesize_english_audio(hint)
        audio_hi = synthesize_hindi_audio(hint)

        return jsonify({
            "audio_en": audio_en,
            "audio_hi": audio_hi
        })
    except Exception as e:
        print(f"[HINT AUDIO ERROR]: {e}")
        return jsonify({
            "audio_en": "",
            "audio_hi": "",
            "error": "❌ Failed to generate hint audio."
        })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

