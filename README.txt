# Un lundi sous surveillance — Analyse de la qualité de l’air

### Réalisé par **Angela TCHING**
Projet EFREI Paris — Module Data Analysis & Visualization

---

## Objectif du projet

Ce projet a pour but d’analyser la **qualité de l’air en France** à partir des données ouvertes du **flux E2 (Geod’air – data.gouv.fr)**.  
L’objectif est de comprendre si **les activités humaines influencent la pollution atmosphérique entre la période estivale (août)** et **la rentrée (septembre)**.

Les données utilisées proviennent de :
https://www.data.gouv.fr/fr/datasets/donnees-temps-reel-de-mesure-des-concentrations-de-polluants-atmospheriques-reglementes-1/

> **Problématique :**  
> Les activités humaines influencent-elles la qualité de l’air entre la période estivale et la rentrée ?

---

## Installation et exécution

### Activer l’environnement virtuel
.venv\Scripts\activate        # Sous Windows
source .venv/bin/activate     # Sous Mac/Linux

### Intallation des requirements
pip install -r requirements.txt

### Préparer les données
python merge_data.py

##Lien Streamlit
https://angelatchg-projet-datav-app-yxxobc.streamlit.app/

##Lien Github
https://github.com/Angelatchg/Projet_DataV


### Lancer Streamlit
streamlit run app.py

