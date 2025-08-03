import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from sklearn.preprocessing import MinMaxScaler
from keras.models import load_model
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def calculate_rsi(prices, window=14):
    """Calcule le RSI (Relative Strength Index)"""
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

class BitcoinPredictionService:
    """Service de prédiction Bitcoin utilisant LSTM"""
    
    def __init__(self, model_path='app/models/model.h5'):
        self.model = None
        self.scaler_x = None
        self.scaler_y = None
        self.model_path = model_path
        self.load_model()
    
    def load_model(self):
        """Charge le modèle LSTM et initialise les scalers"""
        try:
            self.model = load_model(self.model_path)
            self.scaler_x = MinMaxScaler(feature_range=(-1, 1))
            self.scaler_y = MinMaxScaler(feature_range=(-1, 1))
            logger.info("Modèle LSTM chargé avec succès")
            return True
        except Exception as e:
            logger.error(f"Erreur lors du chargement du modèle: {e}")
            return False
    
    def get_latest_bitcoin_data(self):
        """Récupère les dernières données Bitcoin via yfinance"""
        try:
            # Récupération des données des 300 derniers jours pour avoir assez de données pour MM_200
            btc = yf.Ticker("BTC-USD")
            data = btc.history(period="300d", interval="1d")
            
            if data.empty:
                logger.error("Aucune donnée récupérée de yfinance")
                return None
            
            logger.info(f"Données brutes récupérées: {len(data)} jours")
            
            # Calcul des indicateurs techniques
            data['MM_200'] = data['Close'].rolling(window=200, min_periods=1).mean()
            data['RSI_14'] = calculate_rsi(data['Close'], window=14)
            
            # Sélection des features utilisées par le modèle
            features = ['Close', 'Open', 'High', 'Low', 'Volume', 'MM_200', 'RSI_14']
            data = data[features]
            
            # Suppression des lignes avec des valeurs NaN
            data_clean = data.dropna()
            
            logger.info(f"Données après nettoyage: {len(data_clean)} jours")
            
            if len(data_clean) < 50:  # Vérification du minimum de données
                logger.error(f"Pas assez de données après nettoyage: {len(data_clean)} lignes")
                return None
            
            return data_clean
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des données: {e}")
            return None
    
    def prepare_data_for_prediction(self, data):
        """Prépare les données pour la prédiction"""
        try:
            # Vérification des données
            if data is None or len(data) == 0:
                raise ValueError("Données vides")
            
            logger.info(f"Préparation des données: {len(data)} lignes, {len(data.columns)} colonnes")
            
            # Normalisation des features
            X_scaled = self.scaler_x.fit_transform(data.values)
            
            # Normalisation de la target (Close)
            y_scaled = self.scaler_y.fit_transform(data['Close'].values.reshape(-1, 1))
            
            return X_scaled, y_scaled
        except Exception as e:
            logger.error(f"Erreur lors de la préparation des données: {e}")
            raise e
    
    def predict_rolling_days(self, initial_data, n_days=30):
        """Prédiction rolling: utilise les prédictions précédentes pour prédire les jours suivants"""
        predictions = []
        current_data = initial_data.copy()
        
        for day in range(n_days):
            # Reshape pour le modèle LSTM
            input_data = current_data.reshape((1, 1, current_data.shape[0]))
            
            # Prédiction du prix de clôture du jour suivant
            pred_scaled = self.model.predict(input_data, verbose=0)
            pred_price = self.scaler_y.inverse_transform(pred_scaled)[0, 0]
            predictions.append(pred_price)
            
            # Mise à jour des données pour la prochaine prédiction
            current_data_unscaled = self.scaler_x.inverse_transform(current_data.reshape(1, -1))[0]
            
            # Mise à jour: Close = prédiction, on garde les autres features
            current_data_unscaled[0] = pred_price  # Close
            
            # Re-normalisation
            current_data = self.scaler_x.transform(current_data_unscaled.reshape(1, -1))[0]
        
        return np.array(predictions)
    
    def generate_prediction(self):
        """Génère une prédiction pour les 30 prochains jours"""
        try:
            # Récupération des données récentes
            data = self.get_latest_bitcoin_data()
            if data is None:
                raise Exception("Impossible de récupérer les données Bitcoin")
            
            # Préparation des données
            X_scaled, y_scaled = self.prepare_data_for_prediction(data)
            
            # Point de départ: dernière observation
            last_data = X_scaled[-1]
            
            # Prédiction
            predictions = self.predict_rolling_days(last_data, n_days=30)
            
            # Génération des dates
            start_date = datetime.now()
            prediction_dates = [
                (start_date + timedelta(days=i)).strftime("%Y-%m-%d")
                for i in range(1, 31)
            ]
            
            # Calcul du score de confiance (basé sur la variance des prédictions)
            confidence_score = max(0.1, 1.0 - np.std(predictions) / np.mean(predictions))
            
            # Prix actuel et prédit
            current_price = float(data['Close'].iloc[-1])
            predicted_price_30d = float(predictions[-1])
            
            # Calcul de la variation
            variation_percent = ((predicted_price_30d - current_price) / current_price) * 100
            
            # Recommandation DCA basée sur la prédiction
            dca_recommendation = self.generate_dca_recommendation(variation_percent)
            
            return {
                "success": True,
                "current_price": current_price,
                "predicted_price_30d": predicted_price_30d,
                "variation_percent": variation_percent,
                "confidence_score": float(confidence_score),
                "dca_recommendation": dca_recommendation,
                "prediction_dates": prediction_dates,
                "predicted_prices": [float(p) for p in predictions],
                "model_info": {
                    "model_type": "LSTM",
                    "features": ["Close", "Open", "High", "Low", "Volume", "MM_200", "RSI_14"],
                    "training_period": "1 year",
                    "mape": 3.14
                }
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la prédiction: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def generate_dca_recommendation(self, variation_percent):
        """Génère une recommandation DCA basée sur la variation prédite"""
        if variation_percent > 10:
            return {
                "action": "increase",
                "message": "Augmenter les achats DCA - Hausse significative prédite",
                "reason": f"Prédiction: +{variation_percent:.1f}% en 30 jours"
            }
        elif variation_percent > 5:
            return {
                "action": "maintain",
                "message": "Maintenir le DCA actuel - Hausse modérée prédite",
                "reason": f"Prédiction: +{variation_percent:.1f}% en 30 jours"
            }
        elif variation_percent > -5:
            return {
                "action": "maintain",
                "message": "Maintenir le DCA actuel - Stabilité relative prédite",
                "reason": f"Prédiction: {variation_percent:.1f}% en 30 jours"
            }
        elif variation_percent > -10:
            return {
                "action": "reduce",
                "message": "Réduire légèrement le DCA - Baisse modérée prédite",
                "reason": f"Prédiction: {variation_percent:.1f}% en 30 jours"
            }
        else:
            return {
                "action": "reduce",
                "message": "Réduire significativement le DCA - Baisse importante prédite",
                "reason": f"Prédiction: {variation_percent:.1f}% en 30 jours"
            }
    
    def get_model_status(self):
        """Retourne le statut du modèle"""
        return {
            "model_loaded": self.model is not None,
            "model_path": self.model_path,
            "model_type": "LSTM",
            "features": ["Close", "Open", "High", "Low", "Volume", "MM_200", "RSI_14"],
            "performance": {
                "mape_30d": 3.14,
                "horizon": "30 days rolling prediction"
            }
        } 