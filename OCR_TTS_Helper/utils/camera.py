import cv2
import time
import tkinter as tk

def capture_photo(save_path="captured.jpg"):
    """
    Kameradan görüntü alır, SPACE ile fotoğraf çeker, ESC ile çıkılır.
    """
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
    """
    Kameradan canlı görüntü alır, 1 saniyede bir OCR yapar ve sonucu seslendirir.
    Aynı metin tekrar edilmez, hatalar seslendirilmez.
    """
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
            text = ocr_function(frame, lang=lang_ocr)

            if text and text.strip() != prev_text and not text.startswith("Hata:"):
                prev_text = text.strip()
                print(f"Algılanan Metin: {text}")

                if display_label:
                    display_label.after(0, display_label.config, {'text': text.strip()})

                tts_function(text, lang=lang_tts, engine_type=engine_type, rate=rate)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
