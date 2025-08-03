#!/usr/bin/env python3
"""
Script de démarrage pour l'API Flask Bitcoin Prediction
"""

import sys
import os
import logging
from pathlib import Path

# Ajout du chemin du backend au PYTHONPATH
sys.path.append(os.path.join(os.path.dirname(__file__), 'app', 'backend'))

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('backend.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def check_dependencies():
    """Vérifie que toutes les dépendances sont disponibles"""
    try:
        import flask
        import flask_cors
        import numpy
        import pandas
        import yfinance
        import sklearn
        import tensorflow
        import keras
        logger.info("Toutes les dépendances sont disponibles")
        return True
    except ImportError as e:
        logger.error(f"Dépendance manquante: {e}")
        return False

def check_model_file():
    """Vérifie que le fichier modèle existe"""
    model_path = Path("app/models/model.h5")
    if model_path.exists():
        logger.info(f"Modèle trouvé: {model_path}")
        return True
    else:
        logger.error(f"Modèle non trouvé: {model_path}")
        return False

def main():
    """Fonction principale de démarrage"""
    print("Démarrage de l'API Flask Bitcoin Prediction")
    print("=" * 50)
    
    # Vérifications préalables
    logger.info("Vérification des prérequis...")
    
    if not check_dependencies():
        print("Erreur: Dépendances manquantes")
        print("Exécutez: pip install flask flask-cors numpy pandas yfinance scikit-learn tensorflow")
        sys.exit(1)
    
    if not check_model_file():
        print("Erreur: Fichier modèle non trouvé")
        print("Assurez-vous que le modèle est dans le dossier 'app/models/'")
        sys.exit(1)
    
    print("Toutes les vérifications sont passées")
    print("\nDémarrage du serveur API...")
    print("API disponible sur: http://localhost:5001")
    print("Documentation: http://localhost:5001/")
    print("\nPour arrêter: Ctrl+C")
    print("=" * 50)
    
    try:
        # Import et démarrage de l'API Flask
        from api import app
        app.run(host="0.0.0.0", port=5001, debug=False)
    except KeyboardInterrupt:
        print("\nArrêt de l'API...")
        logger.info("API arrêtée par l'utilisateur")
    except Exception as e:
        logger.error(f"Erreur lors du démarrage: {e}")
        print(f"Erreur: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 