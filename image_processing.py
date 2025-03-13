import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import requests
from io import BytesIO
import logging
from text_processing import contiene_numero_telefono

# Configura il logging
logging.basicConfig(level=logging.INFO)

# Whitelist di numeri da ignorare
WHITELIST_NUMERI = ["+39 800", "123456", "000 000 0000"]  

def scarica_immagine(url):
    """Scarica un'immagine da un URL e la restituisce come oggetto PIL Image."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return Image.open(BytesIO(response.content))
    except requests.RequestException as e:
        logging.error(f"Errore durante il download dell'immagine: {e}")
        return None

def preprocessa_immagine(immagine):
    """Applica filtri per migliorare la qualità dell'OCR."""
    try:
        immagine = immagine.convert("L")
        immagine = immagine.filter(ImageFilter.MedianFilter())
        enhancer = ImageEnhance.Contrast(immagine)
        immagine = enhancer.enhance(2)
        return immagine
    except Exception as e:
        logging.error(f"Errore nella pre-elaborazione dell'immagine: {e}")
        return immagine

def estrai_testo(immagine):
    """Estrai testo da un'immagine usando Tesseract OCR con configurazioni avanzate."""
    if immagine is None:
        return ""
    
    immagine = preprocessa_immagine(immagine)

    try:
        custom_oem_psm_config = r'--oem 3 --psm 6'
        testo = pytesseract.image_to_string(immagine, lang="eng+ita", config=custom_oem_psm_config)
        return testo.strip()
    except Exception as e:
        logging.error(f"Errore nell'estrazione del testo: {e}")
        return ""

from discord_notifications import invia_notifica_discord

def analizza_immagine(url):
    """Scarica e analizza un'immagine alla ricerca di numeri di telefono."""
    immagine = scarica_immagine(url)
    
    if not immagine:
        logging.warning("Immagine non valida o non scaricata correttamente.")
        return False

    testo = estrai_testo(immagine)
    logging.info(f"🔍 Testo estratto dall'immagine: {testo}")
    
    invia_notifica_discord(f"📸 **Analisi immagine:**\n🔗 {url}\n📜 **Testo estratto:** `{testo}`")

    if any(num in testo for num in WHITELIST_NUMERI):
        logging.info(f"🟡 Numero in whitelist rilevato: {testo}, nessuna azione.")
        return False
    
    if contiene_numero_telefono(testo):
        logging.info("🔴 Numero di telefono rilevato, rimozione in corso.")
        invia_notifica_discord(f"🚨 **Numero di telefono rilevato in un'immagine!**\n🔗 {url}")
        return True

    logging.info("✅ Nessun numero rilevato, nessuna azione.")
    return False
