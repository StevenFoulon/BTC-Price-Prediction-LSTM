from flask import Flask, jsonify, request
from flask_cors import CORS
import logging
from services.prediction_service import BitcoinPredictionService

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialisation de Flask
app = Flask(__name__)
CORS(app)  # Permet les requêtes CORS pour Streamlit

# Initialisation du service de prédiction
prediction_service = BitcoinPredictionService()

@app.route('/')
def root():
    """Endpoint racine"""
    return jsonify({
        "message": "Bitcoin Prediction API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "predict": "/predict",
            "model_status": "/model/status"
        }
    })

@app.route('/health')
def health_check():
    """Vérification de la santé de l'API"""
    return jsonify({
        "status": "healthy",
        "model_loaded": prediction_service.model is not None,
        "timestamp": prediction_service.get_model_status()
    })

@app.route('/model/status')
def model_status():
    """Statut du modèle LSTM"""
    return jsonify(prediction_service.get_model_status())

@app.route('/predict', methods=['POST'])
def predict():
    """Génère une prédiction Bitcoin pour les 30 prochains jours"""
    try:
        # Génération de la prédiction
        result = prediction_service.generate_prediction()
        
        if result["success"]:
            return jsonify({
                "success": True,
                "data": result
            })
        else:
            return jsonify({
                "success": False,
                "error": result["error"]
            }), 500
            
    except Exception as e:
        logger.error(f"Erreur lors de la prédiction: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/predict', methods=['GET'])
def predict_get():
    """Endpoint GET pour la prédiction (pour compatibilité)"""
    return predict()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False) 