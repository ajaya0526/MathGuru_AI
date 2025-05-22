from utils.tts import synthesize_english_audio, synthesize_hindi_audio

# Sample text to test
text = "Solve 4x + 3 = 11"

print("Testing English TTS...")
english_path = synthesize_english_audio(text)
print(f"✅ English audio saved at: {english_path}")

print("\nTesting Hindi TTS...")
hindi_path = synthesize_hindi_audio(text)
print(f"✅ Hindi audio saved at: {hindi_path}")
