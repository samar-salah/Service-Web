# ServiceEstimationBien.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3

app = FastAPI()
db_path = "BD_Banque.db"

class EstimationBienRequest(BaseModel):
    description: str

def estimer_prix_bien(description: str):
    print(f'desc reçu  : ',description); 
    try:
        with sqlite3.connect(db_path) as connection:
            cursor = connection.cursor()

            query = "SELECT prix FROM VentesRecentesBien WHERE description = ?;"
            cursor.execute(query, (description,))
            print(f"Requête SQL exécutée : {query}")

            prix_bien = cursor.fetchone()
            print(f"Prix bien trouvé : {prix_bien}")

            if prix_bien is not None:  # Vérifier si prix_bien n'est pas None
                return {"prix_estime": prix_bien}
            else:
                raise HTTPException(status_code=404, detail="Bien non trouvé dans la base de données")
    except Exception as e:
        print(f"Erreur lors de l'estimation du bien : {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de l'estimation du bien")

@app.post("/estimate_price/")
async def estimate_price(request: EstimationBienRequest):
    try:
        result = estimer_prix_bien(request.description)
        return result
    except HTTPException as e:
        raise e
