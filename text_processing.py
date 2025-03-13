import re

def contiene_numero_telefono(testo):
    """ Controlla se il testo contiene un numero di telefono. """
    pattern = r"""
        (?:(?:\+|00)\d{1,3}[-.\s]?)?   # Prefisso internazionale opzionale (+39, 0044, ecc.)
        (?:\(?\d{2,4}\)?[-.\s]?)?       # Prefisso nazionale opzionale (02, 055, ecc.)
        \d{3,4}[-.\s]?\d{3,4}           # Numero principale (min 6 cifre totali)
        (?:\s*(?:ext|x|interno)\s*\d+)? # Estensione opzionale (x123, interno 456)
    """
    return re.search(pattern, testo, re.VERBOSE) is not None
