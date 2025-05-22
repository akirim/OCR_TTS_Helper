import tkinter as tk
from tkinter import messagebox, ttk, filedialog
from utils.camera import capture_photo, live_ocr
from utils.ocr import ocr_from_file, ocr_from_frame
from utils.tts import speak_text, stop_speaking
from utils.tts import show_temp_popup
from utils.tts import clear_tts_cache

from PIL import Image
import numpy as np
import time
import re
import pygame



# --- Global ayarlar (seçim kutularından güncelleniyor) ---
settings = {
    "engine": "gtts",
    "lang_tts": "tr",
    "rate": 150
}

spoken_texts = []  # Seslendirilen metinleri sakla


def normalize_text(text):
    return re.sub(r'[^\w]+', '', text).lower().strip()

def get_speaking_lambda():
    last_spoken = {'text': '', 'time': 0}

    def speak_once(text, lang, engine_type, rate, **kwargs):
        norm_text = normalize_text(text)
        now = time.time()
        if (norm_text != normalize_text(last_spoken['text']) or now - last_spoken['time'] > 5) and not pygame.mixer.music.get_busy():
            speak_text(text, lang=lang, engine_type=engine_type, rate=rate, temp_mode=True)
            last_spoken['text'] = text
            last_spoken['time'] = now

    return speak_once

def run_photo_mode():
    try:
        photo_path = capture_photo("foto_gui.jpg")
        text = ocr_from_file(photo_path)
        if text.strip():
            text_output.delete(1.0, tk.END)
            text_output.insert(tk.END, text)
            speak_text(text, lang=settings["lang_tts"], engine_type=settings["engine"], rate=settings["rate"])
        else:
            messagebox.showinfo("Sonuç", "Hiç metin algılanamadı.")
    except Exception as e:
        messagebox.showerror("Hata", str(e))

    if text.strip():
        spoken_texts.append(text.strip())  # Geçmişe ekle



def run_live_mode():
    try:
        live_ocr(
            ocr_from_frame,
            get_speaking_lambda(),
            lang_ocr=lang_tts_var.get(),
            lang_tts=settings["lang_tts"],
            engine_type=settings["engine"],
            rate=settings["rate"]
        )
    except Exception as e:
        messagebox.showerror("Hata", str(e))



def run_image_file():
    try:
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg *.png")])
        if not file_path:
            return

        img = Image.open(file_path)
        text = ocr_from_file(np.array(img))

        if text.strip():
            text_output.delete(1.0, tk.END)
            text_output.insert(tk.END, text)
            speak_text(text, lang=settings["lang_tts"], engine_type=settings["engine"], rate=settings["rate"])
        else:
            messagebox.showinfo("Sonuç", "Hiç metin algılanamadı.")
    except Exception as e:
        messagebox.showerror("Hata", str(e))
    if text.strip():
        spoken_texts.append(text.strip())  # Geçmişe ekle

def show_history():
    if not spoken_texts:
        messagebox.showinfo("Geçmiş", "Henüz seslendirilen bir metin yok.")
        return

    history_win = tk.Toplevel(root)
    history_win.title("📜 Sesli Okuma Geçmişi")
    history_win.geometry("350x300")

    listbox = tk.Listbox(history_win)
    listbox.pack(fill="both", expand=True, padx=10, pady=10)

    for item in spoken_texts[::-1]:
        listbox.insert(tk.END, item[:80] + ("..." if len(item) > 80 else ""))  # Önizleme

    def play_selected():
        index = listbox.curselection()
        if index:
            speak_text(spoken_texts[::-1][index[0]], lang=settings["lang_tts"], engine_type=settings["engine"], rate=settings["rate"])

    tk.Button(history_win, text="▶️ Seçili Metni Oku", command=play_selected).pack(pady=5)


def update_settings():
    settings["engine"] = engine_var.get()
    settings["lang_tts"] = lang_tts_var.get()
    try:
        settings["rate"] = int(rate_var.get())
    except:
        settings["rate"] = 150

# === Tkinter GUI ===
root = tk.Tk()
root.title("OCR + Sesli Okuma (EasyOCR)")
root.geometry("400x650")

# --- Seçim kutuları (motor, dil, hız) ---
tk.Label(root, text="Motor Seçimi").pack()
engine_var = tk.StringVar(value="gtts")
ttk.Combobox(root, textvariable=engine_var, values=["gtts", "pyttsx3"]).pack(pady=5)

tk.Label(root, text="Ses Dili").pack()
lang_tts_var = tk.StringVar(value="tr")
ttk.Combobox(root, textvariable=lang_tts_var, values=["tr", "en"]).pack(pady=5)

tk.Label(root, text="Konuşma Hızı (pyttsx3 için)").pack()
rate_var = tk.StringVar(value="150")
tk.Entry(root, textvariable=rate_var).pack(pady=5)

# --- Butonlar ---
tk.Button(root, text="📷 Fotoğraf Çek", command=lambda: [update_settings(), run_photo_mode()], font=("Arial", 12)).pack(pady=10)
tk.Button(root, text="🖼 Görsel Yükle", command=lambda: [update_settings(), run_image_file()], font=("Arial", 12)).pack(pady=10)
tk.Button(root, text="🎥 Kamera Modu (Canlı OCR)", command=lambda: [update_settings(), run_live_mode()], font=("Arial", 12)).pack(pady=10)
tk.Button(root, text="🔁 Konuşmayı Yeniden Başlat", command=lambda: speak_text(text_output.get(1.0, tk.END).strip(), lang=settings["lang_tts"], engine_type=settings["engine"], rate=settings["rate"]), font=("Arial", 12)).pack(pady=10)
tk.Button(root, text="📜 Geçmişi Göster", command=show_history, font=("Arial", 12)).pack(pady=10)
tk.Button(root, text="😑 Konuşmayı Durdur", command=stop_speaking, font=("Arial", 12)).pack(pady=10)
tk.Button(root, text="🧹 Önbelleği Temizle", command=lambda: [clear_tts_cache(), show_temp_popup("Başarılı", "✅ Önbellek temizlendi", duration=1500)], font=("Arial", 12)).pack(pady=10)

# --- Metin çıktısı ---
tk.Label(root, text="Algılanan Metin").pack()
text_output = tk.Text(root, height=10, wrap="word")
text_output.pack(padx=10, pady=10, fill="both", expand=True)

root.mainloop()
