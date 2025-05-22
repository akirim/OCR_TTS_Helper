import cv2
import time
import re
import tkinter as tk

def preprocess_image(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    thresh = cv2.adaptiveThreshold(
        blur, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY, 11, 2
    )
    return thresh

def clean_text(text):
    return re.sub(r'[^a-zA-Z0-9çğıöşüÇĞİÖŞÜ\s]', '', text)

def capture_photo(save_path="captured.jpg"):
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise Exception("Kamera açılamadı.")

    print("Kamera açıldı. SPACE ile fotoğraf çek, ESC ile iptal et.")

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        cv2.imshow("Fotoğraf Çek - SPACE: Çek | ESC: Çık", frame)
        key = cv2.waitKey(1)

        if key == 27:  # ESC tuşu
            print("İptal edildi.")
            break
        elif key == 32:  # SPACE tuşu
            cv2.imwrite(save_path, frame)
            print(f"Fotoğraf kaydedildi: {save_path}")
            break

    cap.release()
    cv2.destroyAllWindows()
    return save_path

def live_ocr(
    ocr_function,
    tts_function,
    lang_ocr="tr",
    lang_tts="tr",
    engine_type="gtts",
    rate=150,
    display_label=None
):
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise Exception("Kamera açılamadı.")

    prev_text = ""
    last_ocr_time = time.time()

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        cv2.imshow("Kamera - Q'ya basarak çık", frame)

        if time.time() - last_ocr_time > 2.0:
            last_ocr_time = time.time()

            # ✅ Ön işleme uygulanıyor
            processed = preprocess_image(frame)

            # OCR fonksiyonuna işlenmiş görüntü veriliyor
            text = ocr_function(processed, lang=lang_ocr)

            if text and text.strip() != prev_text and not text.startswith("Hata:"):
                # ✅ Metin temizleniyor
                cleaned = clean_text(text.strip())
                prev_text = cleaned

                print(f"Algılanan Metin: {cleaned}")

                if display_label:
                    display_label.after(0, display_label.config, {'text': cleaned})

                tts_function(cleaned, lang=lang_tts, engine_type=engine_type, rate=rate)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
