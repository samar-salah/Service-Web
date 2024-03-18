from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import re
import sqlite3

app = FastAPI()
db_path = "BD_Banque.db"

class DemandePret(BaseModel):
    content: str

class ServiceExtraction:
    def __init__(self, db_path="BD_Banque.db"):
        self.db_path = db_path
        self.create_table()

    def create_table(self):
        try:
            with sqlite3.connect(self.db_path) as connection:
                cursor = connection.cursor()

                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS DemandePret (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nom TEXT,
                        adresse TEXT,
                        montantPret REAL,
                        DescriptionProp TEXT,
                        RevenuMensuel REAL,
                        DepensesMensuel REAL
                    );
                """)

                connection.commit()
                print("Table créée avec succès.")
        except Exception as e:
            print(f"Erreur lors de la création de la table : {e}")

    def extract_info_from_content(self, content):
        identifiant = self.extract_value(content, "Identifiant du Client :")
        nom = self.extract_value(content, "Nom du Client :")
        adresse = self.extract_value(content, "Adresse :")
        montant_pret = self.extract_value(content, "Montant du Prêt Demandé :")
        description_prop = self.extract_value(content, "Description de la Propriété :")
        revenu_mensuel = self.extract_value(content, "Revenu Mensuel :")
        depenses_mensuelles = self.extract_value(content, "Dépenses Mensuelles :")
        
        return identifiant, nom, adresse, float(montant_pret.rstrip(" EUR")), description_prop, float(revenu_mensuel.rstrip(" EUR")), float(depenses_mensuelles.rstrip(" EUR"))

    def extract_value(self, content, keyword):
        match = re.search(f"{re.escape(keyword)}(.+?)(?:\n|$)", content)
        return match.group(1).strip() if match else ""

    def add_to_database(self, identifiant, nom, adresse, montant_pret, description_prop, revenu_mensuel, depenses_mensuelles):
        try:
            with sqlite3.connect(self.db_path) as connection:
                cursor = connection.cursor()

                query = """
                    INSERT INTO DemandePret (nom, adresse, montantPret, DescriptionProp, RevenuMensuel, DepensesMensuel)
                    VALUES (?, ?, ?, ?, ?, ?);
                """
                 
                cursor.execute(query, (nom, adresse, montant_pret, description_prop, revenu_mensuel, depenses_mensuelles))
                
                connection.commit()
                print("Enregistrement ajouté avec succès à la base de données.")
        except Exception as e:
            print(f"Erreur lors de l'ajout à la base de données : {e}")

@app.post("/extract_and_add_to_db/")
async def extract_and_add_to_db(request: DemandePret):
    extraction_service = ServiceExtraction()
    try:
        identifiant, nom, adresse, montant_pret, description_prop, revenu_mensuel, depenses_mensuelles = extraction_service.extract_info_from_content(request.content)
        extraction_service.add_to_database(identifiant, nom, adresse, montant_pret, description_prop, revenu_mensuel, depenses_mensuelles)
        return {"message": "Informations extraites et ajoutées à la base de données avec succès."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'extraction et de l'ajout à la base de données : {e}")
