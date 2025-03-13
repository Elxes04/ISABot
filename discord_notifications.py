import requests
import logging
import configparser

config = configparser.ConfigParser(interpolation=None)
config.read('config.ini')

WEBHOOK_URL = config["discord"].get("webhook_url", "").strip()

def invia_notifica_discord(messaggio):
    """Invia una notifica al webhook Discord."""
    if not WEBHOOK_URL:
        logging.warning("⚠️ Webhook Discord non configurato.")
        return
    
    payload = {
        "content": messaggio
    }
    
    try:
        response = requests.post(WEBHOOK_URL, json=payload)
        if response.status_code != 204:
            logging.error(f"❌ Errore nell'invio della notifica Discord: {response.text}")
    except requests.RequestException as e:
        logging.error(f"❌ Errore di connessione al webhook Discord: {e}")
