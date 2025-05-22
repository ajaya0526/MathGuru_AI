import os
import time
import socket
from gtts import gTTS
import pyttsx3
from googletrans import Translator  # pip install googletrans==4.0.0-rc1

# 🌐 Check internet availability
def is_internet_available():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=2)
        return True
    except:
        return False

# ======================
# 🔊 English TTS Generator (online/offline)
# ======================
def synthesize_english_audio(text):
    try:
        if is_internet_available():
            tts = gTTS(text=text, lang='en', slow=False)
            filename = f"static/audio/eng_{int(time.time())}.mp3"
            tts.save(filename)
            return filename
        else:
            return synthesize_offline_audio(text, lang='en', prefix='eng')
    except Exception as e:
        print(f"[ENGLISH TTS ERROR]: {e}")
        return ""

# ======================
# 🔊 Hindi TTS Generator (online/offline)
# ======================
def synthesize_hindi_audio(text):
    try:
        if is_internet_available():
            translator = Translator()
            translated = translator.translate(text, dest='hi').text
            print("[Translated to Hindi]:", translated)

            tts = gTTS(text=translated, lang='hi', slow=False)
            filename = f"static/audio/hindi_{int(time.time())}.mp3"
            tts.save(filename)
            return filename
        else:
            return synthesize_offline_audio(text, lang='hi', prefix='hindi')
    except Exception as e:
        print(f"[HINDI TTS ERROR]: {e}")
        return ""

# ======================
# 🔇 Offline TTS fallback using pyttsx3
# ======================
def synthesize_offline_audio(text, lang='en', prefix='offline'):
    try:
        engine = pyttsx3.init()
        engine.setProperty('rate', 140)

        voices = engine.getProperty('voices')
        selected = False

        for voice in voices:
            try:
                lang_code = voice.languages[0].decode('utf-8') if isinstance(voice.languages[0], bytes) else voice.languages[0]
                if (lang == 'hi' and 'hi' in lang_code.lower()) or (lang == 'en' and 'en' in lang_code.lower()):
                    engine.setProperty('voice', voice.id)
                    selected = True
                    print(f"✅ Using offline {lang.upper()} voice: {voice.name}")
                    break
            except:
                continue

        if not selected:
            print(f"⚠️ Offline {lang.upper()} voice not found. Using default voice.")

        filename = f"static/audio/{prefix}_{int(time.time())}.mp3"
        engine.save_to_file(text, filename)
        engine.runAndWait()
        return filename
    except Exception as e:
        print(f"[OFFLINE TTS ERROR - {lang.upper()}]: {e}")
        return ""
