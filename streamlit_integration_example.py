import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import time

# Configuration
API_BASE_URL = "http://localhost:5001"

def get_prediction():
    """Récupère la prédiction depuis l'API Flask"""
    try:
        response = requests.post(f"{API_BASE_URL}/predict")
        if response.status_code == 200:
            data = response.json()
            if data["success"]:
                return data["data"]
            else:
                st.error(f"Erreur API: {data.get('error', 'Erreur inconnue')}")
                return None
        else:
            st.error(f"Erreur HTTP: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Erreur de connexion: {e}")
        return None

def check_api_health():
    """Vérifie la santé de l'API"""
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        return response.status_code == 200
    except:
        return False

# Configuration de la page Streamlit
st.set_page_config(
    page_title="Bitcoin Prediction Dashboard",
    page_icon="📈",
    layout="wide"
)

# Titre principal
st.title("📈 Bitcoin Prediction Dashboard")
st.markdown("---")

# Vérification de la santé de l'API
if not check_api_health():
    st.error("⚠️ L'API Flask n'est pas accessible. Assurez-vous qu'elle est démarrée sur http://localhost:5001")
    st.stop()

# Section principale
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("🔮 Prédiction Bitcoin M+30")
    
    # Bouton de génération de prédiction
    if st.button("🔮 Générer Prédiction", type="primary", use_container_width=True):
        with st.spinner("Génération de la prédiction..."):
            prediction_data = get_prediction()
            
            if prediction_data:
                # Affichage des métriques principales
                col1_1, col1_2, col1_3, col1_4 = st.columns(4)
                
                with col1_1:
                    st.metric(
                        "Prix Actuel",
                        f"${prediction_data['current_price']:,.2f}",
                        delta=None
                    )
                
                with col1_2:
                    st.metric(
                        "Prix Prédit J+30",
                        f"${prediction_data['predicted_price_30d']:,.2f}",
                        delta=f"{prediction_data['variation_percent']:.2f}%"
                    )
                
                with col1_3:
                    st.metric(
                        "Variation",
                        f"{prediction_data['variation_percent']:.2f}%",
                        delta=None
                    )
                
                with col1_4:
                    st.metric(
                        "Confiance",
                        f"{prediction_data['confidence_score']:.1%}",
                        delta=None
                    )
                
                # Graphique de prédiction
                st.subheader("📊 Évolution Prédite (30 jours)")
                
                fig = go.Figure()
                
                # Prix actuels (derniers 7 jours)
                dates = pd.date_range(end=datetime.now(), periods=7, freq='D')
                current_prices = [prediction_data['current_price']] * 7
                
                fig.add_trace(go.Scatter(
                    x=dates,
                    y=current_prices,
                    mode='lines+markers',
                    name='Prix Actuel',
                    line=dict(color='blue', width=2)
                ))
                
                # Prix prédits
                prediction_dates = pd.to_datetime(prediction_data['prediction_dates'])
                fig.add_trace(go.Scatter(
                    x=prediction_dates,
                    y=prediction_data['predicted_prices'],
                    mode='lines+markers',
                    name='Prix Prédit',
                    line=dict(color='red', width=2, dash='dash')
                ))
                
                fig.update_layout(
                    title="Prédiction Bitcoin - 30 jours",
                    xaxis_title="Date",
                    yaxis_title="Prix (USD)",
                    hovermode='x unified',
                    height=400
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Stockage des données pour l'affichage dans la colonne de droite
                st.session_state.prediction_data = prediction_data

with col2:
    st.subheader("💡 Recommandation DCA")
    
    if 'prediction_data' in st.session_state:
        prediction_data = st.session_state.prediction_data
        dca_rec = prediction_data['dca_recommendation']
        
        # Affichage de la recommandation
        if dca_rec['action'] == 'increase':
            st.success("📈 AUGMENTER")
            st.info(dca_rec['message'])
        elif dca_rec['action'] == 'maintain':
            st.warning("⏸️ MAINTIEN")
            st.info(dca_rec['message'])
        else:  # reduce
            st.error("📉 RÉDUIRE")
            st.info(dca_rec['message'])
        
        st.markdown(f"**Raison:** {dca_rec['reason']}")
        
        # Informations supplémentaires
        st.markdown("---")
        st.markdown("**Informations Modèle:**")
        st.markdown(f"- Type: {prediction_data['model_info']['model_type']}")
        st.markdown(f"- Features: {len(prediction_data['model_info']['features'])}")
        st.markdown(f"- MAPE: {prediction_data['model_info']['mape']}%")
        st.markdown(f"- Période d'entraînement: {prediction_data['model_info']['training_period']}")
        
        # Bouton de rafraîchissement
        if st.button("🔄 Actualiser", use_container_width=True):
            st.rerun()
    else:
        st.info("Cliquez sur 'Générer Prédiction' pour voir les recommandations")

# Section d'informations
st.markdown("---")
st.subheader("ℹ️ Informations")

col_info1, col_info2 = st.columns(2)

with col_info1:
    st.markdown("**À propos de ce modèle:**")
    st.markdown("""
    - **Modèle LSTM** entraîné sur 1 an de données
    - **7 features** : OHLCV + MM_200 + RSI_14
    - **Performance** : MAPE 3.14% sur 30 jours
    - **Horizon** : Prédiction rolling 30 jours
    """)

with col_info2:
    st.markdown("**Recommandations DCA:**")
    st.markdown("""
    - **Augmenter** : Hausse > 10% prédite
    - **Maintenir** : Variation entre -5% et +10%
    - **Réduire** : Baisse > 5% prédite
    """)

# Footer
st.markdown("---")
st.markdown("*Dernière mise à jour: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "*") 