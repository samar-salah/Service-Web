from ast import Dict
import sqlite3
import requests
import re
db_path = "BD_Banque.db"
def get_score_credit(client_id: int) -> int:
    """
    Récupère le score de crédit en utilisant l'API dans ServiceScore.py.
    """
    # Définir l'URL de l'endpoint FastAPI pour le calcul du score de crédit
    score_endpoint = "http://127.0.0.1:8001/calculate_credit_score/"

    # Envoyer une requête POST à l'API avec l'identifiant du client
    response = requests.post(score_endpoint, json={"identifiant_client": client_id})

    # Vérifier si la requête a réussi (code 200) et extraire le score de crédit
    if response.status_code == 200:
        credit_score = response.json()["credit_score"]
        return credit_score
    else:
        # Si la requête échoue, imprimer le message d'erreur et retourner -1 (ou une valeur appropriée)
        print(f"Erreur lors de la récupération du score de crédit : {response.text}")
        return -1  # Vous pouvez remplacer -1 par une valeur appropriée selon votre logique

def extraire_montant_pret() -> int:
    try:
        with open("demandePret.txt", 'r') as file:
            contenu_demande = file.read()

            # Rechercher le contenu après les deux points de "Montant du Prêt Demandé :"
            match = re.search(r"Montant du Prêt Demandé :(.+?)(?:\n|$)", contenu_demande)
            montant_str = match.group(1).strip() if match else ""

            # Supprimer "EUR" et convertir en entier
            montant_int = int(montant_str.replace(" EUR", ""))
            return montant_int
    except Exception as e:
        print(f"Erreur lors de la lecture du fichier demandePret.txt : {e}")
        return -1  # Vous pouvez choisir une valeur par défaut ou lancer une exception appropriée

def get_valeur_propriete(description: str) -> float:
    """
    Récupère la valeur de propriété en utilisant l'API dans ServiceEstimationBien.py.
    """
    # Définir l'URL de l'endpoint FastAPI pour l'estimation de la valeur de propriété
    estimation_endpoint = "http://127.0.0.1:8002/estimate_price/"

    # Envoyer une requête POST à l'API avec la description de la propriété
    response = requests.post(estimation_endpoint, json={"description": description})

    # Vérifier si la requête a réussi (code 200) et extraire la valeur de propriété
    if response.status_code == 200:
        prix_estimes = response.json()["prix_estime"]
        # Si la valeur retournée est une liste, prenons le premier élément
        valeur_propriete = prix_estimes[0] if isinstance(prix_estimes, list) else prix_estimes
        return float(valeur_propriete)  # Convertir la valeur en float
    else:
        # Si la requête échoue, imprimer le message d'erreur et retourner -1.0 (ou une valeur appropriée)
        print(f"Erreur lors de la récupération de la valeur de propriété : {response.text}")
        return -1.0  
    
def get_montant_dettes(client_id: int) -> float:
    """
    Récupère le montant des dettes en cours depuis la base de données.
    """
    try:
        with sqlite3.connect(db_path) as connection:
            cursor = connection.cursor()

            query = "SELECT dettes_en_cours FROM Client WHERE id = ?;"
            cursor.execute(query, (client_id,))
            montant_dettes = cursor.fetchone()

            # Si la valeur est trouvée, retourner le montant des dettes
            if montant_dettes:
                return float(montant_dettes[0])
            else:
                return -1  # Vous pouvez choisir une valeur par défaut ou lancer une exception appropriée
    except Exception as e:
        print(f"Erreur lors de la récupération du montant des dettes : {e}")
        return -1  # Vous pouvez remplacer -1 par une valeur appropriée selon votre logique

def get_revenu_mensuel(client_id: int) -> int:
    """
    Récupère le revenu mensuel depuis la base de données.
    """
    try:
        with sqlite3.connect(db_path) as connection:
            cursor = connection.cursor()

            query = "SELECT montantPret FROM DemandePret WHERE id = ?;"
            cursor.execute(query, (client_id,))
            revenu_mensuel = cursor.fetchone()

            # Si la valeur est trouvée, retourner le revenu mensuel
            if revenu_mensuel:
                return int(revenu_mensuel[0])
            else:
                return -1  # Vous pouvez choisir une valeur par défaut ou lancer une exception appropriée
    except Exception as e:
        print(f"Erreur lors de la récupération du revenu mensuel : {e}")
        return -1  # Vous pouvez remplacer -1 par une valeur appropriée selon votre logique
    
