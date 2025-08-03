import yfinance as yf
import pandas as pd

print("Test de yfinance...")

# Test de récupération des données
try:
    btc = yf.Ticker("BTC-USD")
    print(f"Ticker créé: {btc}")
    
    # Test avec différentes périodes
    periods = ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"]
    
    for period in periods:
        try:
            data = btc.history(period=period, interval="1d")
            print(f"Période {period}: {len(data)} lignes")
            if len(data) > 0:
                print(f"  Dernière date: {data.index[-1]}")
                print(f"  Prix actuel: ${data['Close'].iloc[-1]:,.2f}")
                break
        except Exception as e:
            print(f"  Erreur avec {period}: {e}")
    
    # Test spécifique avec 200d
    print("\nTest spécifique avec 200d:")
    data = btc.history(period="200d", interval="1d")
    print(f"Données 200d: {len(data)} lignes")
    
    if len(data) > 0:
        print(f"Colonnes disponibles: {list(data.columns)}")
        print(f"Première date: {data.index[0]}")
        print(f"Dernière date: {data.index[-1]}")
        print(f"Prix actuel: ${data['Close'].iloc[-1]:,.2f}")
        
        # Test des indicateurs techniques
        data['MM_200'] = data['Close'].rolling(window=200).mean()
        data['RSI_14'] = calculate_rsi(data['Close'], window=14)
        
        features = ['Close', 'Open', 'High', 'Low', 'Volume', 'MM_200', 'RSI_14']
        data_clean = data[features].dropna()
        
        print(f"\nDonnées après nettoyage: {len(data_clean)} lignes")
        if len(data_clean) > 0:
            print("SUCCESS: Données disponibles pour la prédiction")
        else:
            print("ERROR: Pas de données après nettoyage")
    else:
        print("ERROR: Aucune donnée récupérée")
        
except Exception as e:
    print(f"Erreur générale: {e}")

def calculate_rsi(prices, window=14):
    """Calcule le RSI (Relative Strength Index)"""
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi 