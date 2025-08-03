import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5001"

def test_health_endpoint():
    """Test de l'endpoint de santé"""
    print("Test de l'endpoint /health...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"SUCCESS: Health check réussi")
            print(f"   Status: {data['status']}")
            print(f"   Modèle chargé: {data['model_loaded']}")
            return True
        else:
            print(f"ERROR: Health check échoué: {response.status_code}")
            return False
    except Exception as e:
        print(f"ERROR: Erreur lors du health check: {e}")
        return False

def test_root_endpoint():
    """Test de l'endpoint racine"""
    print("\nTest de l'endpoint racine...")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            data = response.json()
            print(f"SUCCESS: Endpoint racine accessible")
            print(f"   Message: {data['message']}")
            print(f"   Version: {data['version']}")
            return True
        else:
            print(f"ERROR: Endpoint racine échoué: {response.status_code}")
            return False
    except Exception as e:
        print(f"ERROR: Erreur lors du test racine: {e}")
        return False

def test_model_status():
    """Test de l'endpoint de statut du modèle"""
    print("\nTest de l'endpoint /model/status...")
    try:
        response = requests.get(f"{BASE_URL}/model/status")
        if response.status_code == 200:
            data = response.json()
            print(f"SUCCESS: Statut du modèle récupéré")
            print(f"   Type: {data['model_type']}")
            print(f"   Features: {len(data['features'])} features")
            print(f"   MAPE 30j: {data['performance']['mape_30d']}%")
            return True
        else:
            print(f"ERROR: Statut modèle échoué: {response.status_code}")
            return False
    except Exception as e:
        print(f"ERROR: Erreur lors du test statut modèle: {e}")
        return False

def test_predict_endpoint():
    """Test de l'endpoint de prédiction"""
    print("\nTest de l'endpoint /predict...")
    try:
        response = requests.post(f"{BASE_URL}/predict")
        if response.status_code == 200:
            data = response.json()
            if data["success"]:
                prediction_data = data["data"]
                print(f"SUCCESS: Prédiction générée")
                print(f"   Prix actuel: ${prediction_data['current_price']:,.2f}")
                print(f"   Prix prédit J+30: ${prediction_data['predicted_price_30d']:,.2f}")
                print(f"   Variation: {prediction_data['variation_percent']:.2f}%")
                print(f"   Confiance: {prediction_data['confidence_score']:.2%}")
                print(f"   Recommandation DCA: {prediction_data['dca_recommendation']['action']}")
                print(f"   Message: {prediction_data['dca_recommendation']['message']}")
                return True
            else:
                print(f"ERROR: Prédiction échouée: {data.get('error', 'Erreur inconnue')}")
                return False
        else:
            print(f"ERROR: Prédiction échoué: {response.status_code}")
            print(f"   Réponse: {response.text}")
            return False
    except Exception as e:
        print(f"ERROR: Erreur lors du test prédiction: {e}")
        return False

def run_performance_test():
    """Test de performance de l'API"""
    print("\nTest de performance...")
    
    start_time = time.time()
    success_count = 0
    total_requests = 3
    
    for i in range(total_requests):
        try:
            response = requests.post(f"{BASE_URL}/predict")
            if response.status_code == 200:
                success_count += 1
            print(f"   Requête {i+1}/{total_requests}: {response.status_code}")
        except Exception as e:
            print(f"   Requête {i+1}/{total_requests}: Erreur - {e}")
    
    end_time = time.time()
    avg_time = (end_time - start_time) / total_requests
    
    print(f"SUCCESS: Test de performance terminé")
    print(f"   Requêtes réussies: {success_count}/{total_requests}")
    print(f"   Temps moyen par requête: {avg_time:.2f}s")
    print(f"   Taux de succès: {success_count/total_requests:.1%}")
    
    return success_count == total_requests

def main():
    """Fonction principale de test"""
    print("Démarrage des tests de l'API Flask Bitcoin Prediction")
    print("=" * 60)
    
    # Attendre que l'API soit prête
    print("Attente du démarrage de l'API...")
    time.sleep(3)
    
    # Tests
    tests = [
        test_root_endpoint,
        test_health_endpoint,
        test_model_status,
        test_predict_endpoint,
        run_performance_test
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result if result is not None else False)
        except Exception as e:
            print(f"ERROR: Erreur lors du test: {e}")
            results.append(False)
    
    # Résumé
    print("\n" + "=" * 60)
    print("RESUME DES TESTS")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Tests réussis: {passed}/{total}")
    print(f"Taux de succès: {passed/total:.1%}")
    
    if passed == total:
        print("SUCCESS: Tous les tests sont passés avec succès!")
    else:
        print("WARNING: Certains tests ont échoué")
    
    print("\nRecommandations:")
    if passed == total:
        print("SUCCESS: L'API est prête pour la production")
        print("SUCCESS: Intégration avec Streamlit possible")
    else:
        print("ERROR: Vérifiez les logs de l'API pour plus de détails")
        print("ERROR: Assurez-vous que le modèle est correctement chargé")

if __name__ == "__main__":
    main() 