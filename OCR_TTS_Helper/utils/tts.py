import pyttsx3
from gtts import gTTS
import os
import hashlib
import threading
import pygame
import tkinter as tk
import tempfile
import time
import queue

# Global değişkenler
is_speaking = False
current_engine = None

# TTS kuyruğu ve durumları
tts_queue = queue.Queue()
pyttsx3_thread_started = False

# pygame ses sistemi başlat
pygame.mixer.init()

# Cache klasörü
CACHE_DIR = os.path.join(tempfile.gettempdir(), "tts_cache")
os.makedirs(CACHE_DIR, exist_ok=True)

def show_temp_popup(title, message, duration=1500):
    popup = tk.Toplevel()
    popup.title(title)
    popup.geometry("300x100")
    popup.attributes("-topmost", True)
    label = tk.Label(popup, text=message, font=("Arial", 12))
    label.pack(expand=True)
    popup.after(duration, popup.destroy)

def get_cached_audio_path(text: str, lang: str) -> str:
    hash_key = hashlib.md5(f"{text}_{lang}".encode('utf-8')).hexdigest()
    return os.path.join(CACHE_DIR, f"{hash_key}.mp3")

def pyttsx3_worker():
    global current_engine
    engine = pyttsx3.init()
    current_engine = engine
    while True:
        item = tts_queue.get()
        if item is None:
            break
        text, rate, lang = item
        voices = engine.getProperty("voices")
        for voice in voices:
            if lang == "tr" and "turkish" in voice.name.lower():
                engine.setProperty("voice", voice.id)
                break
            elif lang == "en" and "english" in voice.name.lower():
                engine.setProperty("voice", voice.id)
                break
        engine.setProperty("rate", rate)
        engine.say(text)
        engine.runAndWait()

def threaded_speak_text(text: str, lang="tr", engine_type="gtts", rate=150, notify_prepare=True, temp_mode=False):
    global is_speaking, current_engine
    stop_speaking()
    is_speaking = True

    if engine_type == "gtts":
        if temp_mode:
            fd, path = tempfile.mkstemp(suffix=".mp3")
            os.close(fd)
            try:
                tts = gTTS(text=text, lang=lang)
                tts.save(path)

                if is_speaking:
                    pygame.mixer.music.load(path)
                    pygame.mixer.music.play()
                    pygame.event.pump()
                    while pygame.mixer.music.get_busy():
                        time.sleep(0.1)
            finally:
                if os.path.exists(path):
                    os.remove(path)
        else:
            audio_path = get_cached_audio_path(text, lang)
            if not os.path.exists(audio_path):
                if notify_prepare:
                    show_temp_popup("Bilgi", "🔄 Ses hazırlanıyor, lütfen bekleyin...", duration=1500)
                tts = gTTS(text=text, lang=lang)
                tts.save(audio_path)

            if is_speaking:
                pygame.mixer.music.load(audio_path)
                pygame.mixer.music.play()
                pygame.event.pump()
                time.sleep(0.1)
    else:
        raise ValueError("engine_type 'gtts' veya 'pyttsx3' olmalı.")

def speak_text(text: str, lang="tr", engine_type="gtts", rate=150, notify_prepare=True, temp_mode=False):
    global pyttsx3_thread_started
    if engine_type == "pyttsx3":
        if not pyttsx3_thread_started:
            threading.Thread(target=pyttsx3_worker, daemon=True).start()
            pyttsx3_thread_started = True
        tts_queue.put((text, rate, lang))
    else:
        threading.Thread(
            target=threaded_speak_text,
            args=(text, lang, engine_type, rate, notify_prepare, temp_mode)
        ).start()

def stop_speaking():
    global is_speaking, current_engine
    is_speaking = False
    try:
        if current_engine:
            current_engine.stop()
        pygame.mixer.music.stop()
    except:
        pass

def clear_tts_cache():
    for file_name in os.listdir(CACHE_DIR):
        file_path = os.path.join(CACHE_DIR, file_name)
        try:
            os.remove(file_path)
        except Exception as e:
            print(f"Cache dosyası silinemedi: {e}")
