import pytesseract
from PIL import Image
import requests
from io import BytesIO
import logging
from text_processing import contiene_numero_telefono

# Configura il logging
logging.basicConfig(level=logging.INFO)

def scarica_immagine(url):
    """Scarica un'immagine da un URL e la restituisce come oggetto PIL Image."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return Image.open(BytesIO(response.content))
    except requests.RequestException as e:
        logging.error(f"Errore durante il download dell'immagine: {e}")
        return None

def estrai_testo(immagine):
    """Estrai testo da un'immagine usando Tesseract OCR con configurazioni avanzate."""
    if immagine is None:
        return ""
    
    try:
        immagine = immagine.convert("L")

        custom_oem_psm_config = r'--oem 3 --psm 6'
        testo = pytesseract.image_to_string(immagine, lang="eng+ita", config=custom_oem_psm_config)
        return testo.strip()
    except Exception as e:
        logging.error(f"Errore nell'estrazione del testo: {e}")
        return ""

def analizza_immagine(url):
    """Scarica e analizza un'immagine alla ricerca di numeri di telefono."""
    immagine = scarica_immagine(url)
    
    if not immagine:
        logging.warning("Immagine non valida o non scaricata correttamente.")
        return False

    testo = estrai_testo(immagine)
    logging.info(f"Testo estratto dall'immagine: {testo}")
    
    return contiene_numero_telefono(testo)
