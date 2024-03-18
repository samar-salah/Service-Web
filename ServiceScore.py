import sqlite3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()
db_path = "BD_Banque.db"

class CreditRequest(BaseModel):
    identifiant_client: int

# Fonction pour obtenir les informations d'un client à partir de la base de données
def obtenir_informations_client(identifiant_client: int):
    try:
        with sqlite3.connect(db_path) as connection:
            cursor = connection.cursor()

            query = "SELECT dettes_en_cours, paiements_en_retard, faillite FROM Client WHERE id = ?;"
            cursor.execute(query, (identifiant_client,))
            print(f"Requête SQL exécutée : {query}")

            client_data = cursor.fetchone()
            print(f"Données extraites : {client_data}")

            if client_data:
                dettes, paiements_retard, faillite = client_data
                return dettes, paiements_retard, int(faillite)
            else:
                return None
    except Exception as e:
        print(f"Erreur lors de la récupération des informations du client : {e}")
        return None

# Fonction pour calculer le score de crédit en fonction des informations du client
def calculer_score_credit(identifiant_client: int, dettes: int, paiements_retard: int, faillite: int):
    # Score de base
    score_de_base = 600

    # Pénalités pour différents facteurs
    penalite_dettes_actuelles = 10
    penalite_paiements_en_retard = 20
    penalite_faillite = 100

    # Calcul du score en appliquant les pénalités
    score_dettes = score_de_base - (dettes * penalite_dettes_actuelles)
    score_paiements_en_retard = score_de_base - (paiements_retard * penalite_paiements_en_retard)

    # Si le client a fait faillite, appliquer une pénalité supplémentaire
    score_faillite = score_de_base - penalite_faillite if faillite else score_de_base

    # Calcul du score final comme la moyenne des scores obtenus
    score_final = (score_dettes + score_paiements_en_retard + score_faillite) / 3

    # Limiter le score final entre 300 et 800
    score_final = max(300, min(800, score_final))

    # Renvoyer le score final en tant qu'entier
    return int(score_final)

# Endpoint FastAPI pour calculer le score de crédit
@app.post("/calculate_credit_score/")
async def calculate_credit_score(request: CreditRequest):
    identifiant_client = request.identifiant_client
    client_info = obtenir_informations_client(identifiant_client)

    # Si le client n'est pas trouvé dans la base de données, renvoyer une erreur 404
    if client_info is None:
        raise HTTPException(status_code=404, detail="Client non trouvé")

    # Calcul du score de crédit
    credit_score = calculer_score_credit(identifiant_client, *client_info)

    # Renvoyer le résultat sous la forme d'un dictionnaire JSON
    return {"credit_score": credit_score}
