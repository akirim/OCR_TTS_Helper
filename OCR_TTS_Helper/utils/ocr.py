import easyocr
import cv2
import numpy as np
from PIL import Image

# EasyOCR okuyucusu
reader = easyocr.Reader(['tr', 'en'], gpu=False)

def ocr_from_file(image_path: str, lang="tr", **kwargs) -> str:
    """EasyOCR ile görselden metin çıkar."""
    try:
        results = reader.readtext(image_path, detail=0)
        return "\n".join(results).strip()
    except Exception as e:
        return f"Hata: {e}"

def ocr_from_frame(frame, lang="tr") -> str:
    """EasyOCR ile kareden anlık metin çıkar."""
    try:
        results = reader.readtext(frame, detail=0)
        return "\n".join(results).strip()
    except Exception as e:
        return f"Hata: {e}"