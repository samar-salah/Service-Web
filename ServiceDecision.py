from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class DecisionRequest(BaseModel):
    credit_score: int
    montant_pret: int
    valeur_propriete: float
    montant_dettes: float
    revenu_mensuel: int

@app.post("/make_decision/")
async def make_decision(request: DecisionRequest):
    print("coucou")
    try:
        # Récupérer les valeurs des paramètres
        score_credit = request.credit_score
        montant_pret = request.montant_pret
        valeur_propriete = request.valeur_propriete
        montant_dettes = request.montant_dettes
        revenu_mensuel = request.revenu_mensuel
        
        print(f'infos  recus dans le service ',score_credit,montant_pret,valeur_propriete,montant_dettes,revenu_mensuel)

        if montant_dettes is not None and revenu_mensuel is not None:
            # Étape d'analyse des risques
            if score_credit > 30 and montant_pret <= valeur_propriete:
                risque = "Faible"
            else:
                risque = "Élevé"

            # Calcul du ratio dette/revenu
            ratio_dette_revenu = (montant_dettes / revenu_mensuel) * 100

            # Politiques de l'institution Financière
            # Supposons que la politique exige un score de crédit minimum de 25 et un ratio dette/revenu maximum de 40%
            if score_credit >= 25 and ratio_dette_revenu <= 40:
                politique_interne_satisfait = True
            else:
                politique_interne_satisfait = False

            # Modèles de Prédiction
            # Supposons que le modèle de prédiction retourne une probabilité de défaut (0-100)
            # Nous considérons que 20 ou moins signifie faible risque de défaut

            # Prise de décision
            if score_credit > 30 and montant_pret <= valeur_propriete and politique_interne_satisfait:
                taux_interet = 4.5  # Exemple de taux d'intérêt en pourcentage
                duree_pret = 20  # Exemple de durée du prêt en années
                montant_maximum_accorde = 450000  # Exemple de montant maximum accordé en euros

                taux_interet_str = f"Taux d'intérêt : {taux_interet}%"
                duree_pret_str = f"Durée du prêt : {duree_pret} ans"
                montant_maximum_accorde_str = f"Montant maximum accordé : {montant_maximum_accorde} EUR"

                decision = f"Prêt approuvé, {taux_interet_str}, {duree_pret_str}, {montant_maximum_accorde_str}"
            else:
                decision = "Prêt refusé"

            return {"Décision": decision}
        else:
            return {"Erreur": "Montant des dettes ou revenu mensuel non définis."}

    except Exception as e:
        return {"Erreur": str(e)}
