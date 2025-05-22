import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from utils.feedback import evaluate_and_speak

def test_evaluate_and_speak_valid_expression():
    expression = "10 / 2 + 3"
    audio_path = evaluate_and_speak(expression)

    # ✅ Check if result audio was created
    assert os.path.exists(audio_path)
    assert "feedback_result.mp3" in audio_path

def test_evaluate_and_speak_invalid_expression():
    expression = "5 + $wrong"
    audio_path = evaluate_and_speak(expression)

    # ✅ Should fallback to error audio
    assert audio_path == "static/audio/feedback_error.mp3"
