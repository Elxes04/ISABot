import praw
import configparser

# Lettura del file di configurazione
config = configparser.ConfigParser()
config.read('config.ini')

def connetti_reddit():
    """ Crea una connessione a Reddit usando il file config.ini. """
    return praw.Reddit(
        client_id=config['bot']['client_id'],
        client_secret=config['bot']['client_secret'],
        username=config['bot']['username'],
        password=config['bot']['password'],
        user_agent=config['bot']['user_agent']
    )

def rimuovi_contenuto(contenuto):
    """ Rimuove un post o un commento se configurato. """
    try:
        if isinstance(contenuto, praw.models.Submission) or isinstance(contenuto, praw.models.Comment):
            contenuto.mod.remove()
            print(f"✅ Contenuto {contenuto.id} rimosso.")
    except Exception as e:
        print(f"❌ Errore nella rimozione del contenuto {contenuto.id}: {e}")

def banna_utente(reddit, autore):
    """ Bana un utente per il periodo configurato. """
    try:
        subreddit = reddit.subreddit(config['bot']['subreddit'])
        subreddit.banned.add(
            redditor=str(autore),
            duration=int(config["moderation"]["ban_duration"]),
            note=config["moderation"]["ban_reason"]
        )
        print(f"✅ Utente {autore} bannato per {config['moderation']['ban_duration']} giorni.")
    except Exception as e:
        print(f"❌ Errore nel bannare {autore}: {e}")

def invia_messaggio(reddit, autore):
    """ Invia un messaggio di avviso all'utente. """
    try:
        reddit.redditor(str(autore)).message(
            "Avviso di moderazione",
            config["moderation"]["ban_reason"]
        )
        print(f"📩 Messaggio inviato a {autore}.")
    except Exception as e:
        print(f"❌ Errore nell'invio del messaggio a {autore}: {e}")
