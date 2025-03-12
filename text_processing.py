import re

def contiene_numero_telefono(testo):
    """ Controlla se il testo contiene un numero di telefono. """
    pattern = r"""
        (?:(?:\+|00)\d{1,3}[-.\s]?)?
        (?:\(?\d{2,4}\)?[-.\s]?)?
        \d{3,4}[-.\s]?\d{3,4}
    """
    return re.search(pattern, testo, re.VERBOSE) is not None
