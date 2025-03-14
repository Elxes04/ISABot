import logging
import praw
import time
import configparser
import threading
import prawcore
from moderation import connetti_reddit, rimuovi_contenuto, banna_utente, invia_messaggio
from image_processing import analizza_immagine
from text_processing import contiene_numero_telefono
from discord_notifications import invia_notifica_discord

# Configura il logging
logging.basicConfig(level=logging.INFO)

# Legge il file di configurazione
config = configparser.ConfigParser(interpolation=None)
config.read('config.ini')

def controlla_post(post, reddit):
    """ Analizza un post e applica la moderazione se necessario. """
    try:
        if contiene_numero_telefono(post.title) or contiene_numero_telefono(post.selftext):
            logging.info(f"🔴 Numero di telefono rilevato nel post {post.id}: \"{post.title}\" | \"{post.selftext}\"")
            rimuovi_contenuto(post)
            if config["moderation"].getboolean("ban_user"):
                banna_utente(reddit, post.author)
            else:
                invia_notifica_discord(f"🚨 **Numero di telefono rilevato nel post {post.id}**\n🔗 [Link](https://reddit.com{post.permalink})\n👤 **Autore:** {post.author}")
            invia_messaggio(reddit, post.author)

        if post.url.endswith(("jpg", "jpeg", "png")):
            logging.info(f"📷 Analizzando immagine del post {post.id}...")
            if analizza_immagine(post.url):
                logging.info(f"🔴 Numero di telefono rilevato nell'immagine del post {post.id}.")
                rimuovi_contenuto(post)
                if config["moderation"].getboolean("ban_user"):
                    banna_utente(reddit, post.author)
                else:
                    invia_notifica_discord(f"🚨 **Numero di telefono rilevato nell'immagine del post {post.id}**\n🔗 [Link](https://reddit.com{post.permalink})\n👤 **Autore:** {post.author}")
                invia_messaggio(reddit, post.author)
            else:
                logging.info(f"✅ Nessun numero rilevato nell'immagine del post {post.id}.")
    except Exception as e:
        logging.error(f"❌ Errore nel controllo del post {post.id}: {e}")

def controlla_commento(commento, reddit):
    """ Analizza un commento e applica la moderazione se necessario. """
    try:
        if contiene_numero_telefono(commento.body):
            logging.info(f"🔴 Numero di telefono rilevato nel commento {commento.id}.")
            rimuovi_contenuto(commento)
            if config["moderation"].getboolean("ban_user"):
                banna_utente(reddit, commento.author)
            else:
                invia_notifica_discord(f"🚨 **Numero di telefono rilevato nel commento {commento.id}**\n🔗 [Link](https://reddit.com{commento.permalink})\n👤 **Autore:** {commento.author}")
            invia_messaggio(reddit, commento.author)
    except Exception as e:
        logging.error(f"Errore nel controllo del commento {commento.id}: {e}")

def monitora_post(reddit, subreddit):
    """ Monitora i nuovi post nel subreddit. """
    while True:
        try:
            for post in subreddit.stream.submissions(skip_existing=True):
                controlla_post(post, reddit)
        except prawcore.exceptions.RequestException as e:
            logging.warning(f"⚠️ Connessione persa (post), riconnessione in 10s: {e}")
            time.sleep(10)

def monitora_commenti(reddit, subreddit):
    """ Monitora i nuovi commenti nel subreddit. """
    while True:
        try:
            for commento in subreddit.stream.comments(skip_existing=True):
                controlla_commento(commento, reddit)
        except prawcore.exceptions.RequestException as e:
            logging.warning(f"⚠️ Connessione persa (commenti), riconnessione in 10s: {e}")
            time.sleep(10)

def avvia_bot():
    """ Avvia il bot e monitora i nuovi post e commenti contemporaneamente. """
    try:
        reddit = connetti_reddit()
        subreddit = reddit.subreddit(config["bot"]["subreddit"])
    except Exception as e:
        logging.error(f"Errore di connessione a Reddit: {e}")
        return

    logging.info(f"✅ Bot attivo su r/{config['bot']['subreddit']}...")

    # Avvia due thread: uno per i post e uno per i commenti
    thread_post = threading.Thread(target=monitora_post, args=(reddit, subreddit), daemon=True)
    thread_commenti = threading.Thread(target=monitora_commenti, args=(reddit, subreddit), daemon=True)

    thread_post.start()
    thread_commenti.start()

    # Mantieni il bot attivo
    while True:
        time.sleep(10)

if __name__ == "__main__":
    avvia_bot()
