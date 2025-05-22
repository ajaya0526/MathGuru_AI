import re
import socket
from sympy import sympify
from num2words import num2words
import google.generativeai as genai
from dotenv import load_dotenv

# 🔐 Load environment and configure Gemini
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# 🌐 Check internet status
def is_internet_available():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=2)
        return True
    except:
        return False

# 🧮 Solve expression using sympy (offline)
def solve_expression_offline(expr):
    try:
        expr = expr.replace('^', '**').strip()
        result = sympify(expr, evaluate=True)
        if result is None:
            return None, "❌ Unable to solve"

        numeric_result = float(result)
        if numeric_result.is_integer():
            numeric_result = int(numeric_result)

        expr_words = expression_to_words(expr)
        result_words = num2words(numeric_result)
        spoken = f"{expr_words} equals {result_words}"

        return numeric_result, spoken

    except Exception as e:
        print(f"[OFFLINE SOLVER ERROR]: {e}")
        return None, "❌ Could not evaluate the expression offline"

# 🌐 Solve and explain using Gemini
def solve_expression_online(expr):
    try:
        prompt = f"""
Solve and explain the following math expression for a student:

Expression: {expr}

Format:
🧠 Step-by-step explanation
✅ Final Answer: [result]
"""
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        text = response.text.strip()

        # Try to extract final result
        match = re.search(r"(final answer|answer)\s*[:=]?\s*(.+)", text, re.IGNORECASE)
        result_value = match.group(2).strip() if match else "❓ Unknown"

        return result_value, text

    except Exception as e:
        print(f"[ONLINE SOLVER ERROR]: {e}")
        return "❌", "❌ Could not connect to AI server"

# 🔁 Auto-mode: use Gemini if online, fallback to sympy if offline
def solve_expression(expr):
    if is_internet_available():
        return solve_expression_online(expr)
    else:
        return solve_expression_offline(expr)

# 🔤 Convert math expression to spoken English
def expression_to_words(expr):
    symbols = {
        '**': 'raised to the power of',
        '^': 'to the power of',
        '*': 'times',
        '/': 'divided by',
        '+': 'plus',
        '-': 'minus',
        '=': 'equals',
        '(': 'open bracket',
        ')': 'close bracket'
    }

    expr = expr.replace('**', '^')  # Treat '**' as '^'

    tokens = []
    buffer = ''

    for char in expr:
        if char.isdigit() or char == '.':
            buffer += char
        else:
            if buffer:
                try:
                    tokens.append(num2words(float(buffer)))
                except:
                    tokens.append(buffer)
                buffer = ''
            tokens.append(symbols.get(char, char))

    if buffer:
        try:
            tokens.append(num2words(float(buffer)))
        except:
            tokens.append(buffer)

    spoken = ' '.join(tokens)
    spoken = spoken.replace('^', 'raised to the power of')
    return spoken
