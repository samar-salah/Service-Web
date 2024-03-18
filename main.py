import tkinter as tk
from tkinter import Label, Entry, Button, messagebox
import requests
from infosdecision import extraire_montant_pret, get_montant_dettes, get_revenu_mensuel, get_score_credit, get_valeur_propriete
from pydantic import BaseModel
import re

class CreditRequest(BaseModel):
    identifiant_client: int

class DemandePret(BaseModel):
    content: str

def on_submit():
    try:
        identifiant_client = int(id_entry.get())

        # Accéder au fichier demandePret.txt et lire son contenu
        with open("demandePret.txt", 'r') as file:
            demande_pret_content = file.read()

        # Extraire le contenu après les deux points de "Description de la Propriété :"
        description_prop = extract_description(demande_pret_content)

        # Appeler le serviceExtraction avec le contenu du fichier
        extraction_response = requests.post("http://127.0.0.1:8000/extract_and_add_to_db/", json={"content": demande_pret_content})

        if extraction_response.status_code == 200:
            print("Extraction et ajout à la base de données avec succès.")
        else:
            raise Exception(extraction_response.text)

        # Appeler le serviceScore avec l'identifiant client
        score_response = requests.post("http://127.0.0.1:8001/calculate_credit_score", json={"identifiant_client": identifiant_client})

        if score_response.status_code == 200:
            credit_score = score_response.json()["credit_score"]
        else:
            raise Exception(score_response.text)

        # Appeler le serviceEstimationBien avec la description extraite
        estimation_response = requests.post("http://127.0.0.1:8002/estimate_price/", json={"description": description_prop})

        if estimation_response.status_code == 200:
            estimated_price = estimation_response.json()["prix_estime"]
        else:
            raise Exception(estimation_response.text)

        # Appeler la fonction pour extraire le montant du prêt
        montant_pret = extraire_montant_pret()

        valeur_propriete = get_valeur_propriete(description_prop)

        # Appeler la fonction get_montant_dettes avec l'identifiant client
        montant_dettes = get_montant_dettes(identifiant_client)

        # Appeler la fonction get_revenu_mensuel avec l'identifiant client
        revenu_mensuel = get_revenu_mensuel(identifiant_client)

        # Appeler le service Decision
        decision_response = requests.post("http://127.0.0.1:8003/make_decision/", json={"credit_score": credit_score, "montant_pret": int(montant_pret), "valeur_propriete": valeur_propriete, "montant_dettes": montant_dettes, "revenu_mensuel": revenu_mensuel})

        if decision_response.status_code == 200:
            response_data = decision_response.json()
            result_label.config(text=f"Score de crédit : {credit_score}\nEstimation de prix : {estimated_price} EUR\nMontant du prêt : {montant_pret}\nValeur de propriété : {valeur_propriete}\nMontant des dettes : {montant_dettes} EUR\nRevenu mensuel : {revenu_mensuel} EUR\nDécision prise : {response_data}")
        else:
            raise Exception(decision_response.text)

    except ValueError as ve:
        messagebox.showerror("Erreur de valeur", f"Erreur de valeur : {ve}")
    except Exception as e:
        messagebox.showerror("Erreur lors de l'appel aux services", f"Erreur lors de l'appel aux services : {e}")
        print("Erreur complète :", str(e))

def extract_description(content):
    # Rechercher le contenu après les deux points de "Description de la Propriété :"
    match = re.search(r"Description de la Propriété :(.+?)(?:\n|$)", content)
    return match.group(1).strip() if match else ""

# Interface utilisateur tkinter
root = tk.Tk()
root.title("ServiceScore Client")

# Ajout du titre à l'interface
title_label = Label(root, text="Système de Prêt - Évaluation de Décision", font=("Helvetica", 16, "bold"))
title_label.pack(pady=10)

id_label = Label(root, text="Identifiant du client :")
id_label.pack()

id_entry = Entry(root)
id_entry.pack()

submit_button = Button(root, text="Soumettre", command=on_submit, bg="red", fg="white", padx=10, pady=5)
submit_button.pack(pady=10)

result_label = Label(root, text="", font=("Helvetica", 12))
result_label.pack()

root.mainloop()
