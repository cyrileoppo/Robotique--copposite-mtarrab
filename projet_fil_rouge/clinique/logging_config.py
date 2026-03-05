import logging
import sys

def setup_logger(debug_mode=False):
    """Configure le logger selon les directives du TP."""
    niveau = logging.DEBUG if debug_mode else logging.INFO
    
    formateur = logging.Formatter('[%(asctime)s] %(levelname)s %(name)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    
    logger = logging.getLogger()
    logger.setLevel(niveau)
    
    # Affichage terminal
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formateur)
    logger.addHandler(console_handler)
    
    # Écriture dans un fichier
    file_handler = logging.FileHandler('robot.log')
    file_handler.setFormatter(formateur)
    logger.addHandler(file_handler)
    
    return logger