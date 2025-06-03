
from utils.hints import get_next_hint, reset_conversation

questions = [
    "what is the area of a triangle with base 10 and height 4",
    "find the lcm of 6 and 8",
    "x + 3 = 7",
    "how many apples does Sam have",
    "add 24 and 38",
    "simplify (x + 2)(x + 3)",
    "what is the percentage of 80",
    "6 + 7 * 3",
    "solve the equation 2x + 4 = 10",
    "divide 48 by 6"
]

print("🔌 Offline Hint System Test")
print("-" * 40)

for question in questions:
    print(f"\n🔍 Question: {question}")
    reset_conversation()
    for i in range(3):
        hint = get_next_hint(question)
        print(hint)
