# merge_data.py
from utils.io import load_from_list, save_parquet
from utils.prep import clean_data

FILES = [
    "data/raw/FR_E2_2024-08-05.csv",
    "data/raw/FR_E2_2024-09-02.csv",
    "data/raw/FR_E2_2025-08-04.csv",
    "data/raw/FR_E2_2025-09-01.csv",
]

print("Chargement des 4 lundis...")
df = load_from_list(FILES)
print(f"Brut : {len(df):,} lignes")

print("Nettoyage/harmonisation...")
df_clean = clean_data(df)
print(f"Nettoyé : {len(df_clean):,} lignes, colonnes = {list(df_clean.columns)}")

# Coordonnées par code_zas
ZAS_COORDS = {
    # Grand Est
    "FR44ZAG01": (48.6921, 6.1844),   # ZAG NANCY
    "FR44ZAG02": (49.1194, 6.1808),   # ZAG METZ
    "FR44ZAG03": (48.5790, 7.7519),   # ZAG STRASBOURG
    "FR44ZAG04": (48.7740, 5.1624),   # ZAG BAR-LE-DUC
    "FR44ZAG05": (49.2600, 4.0317),   # ZAG CHARLEVILLE-MÉZIÈRES
    "FR44ZAG06": (48.3000, 4.0833),   # ZAG TROYES
    "FR44ZAG07": (47.6376, 7.3380),   # ZAG MULHOUSE
    "FR44ZAG08": (48.1098, 5.1414),   # ZAG CHAUMONT
    "FR44ZAG09": (48.9500, 4.3333),   # ZAG CHÂLONS-EN-CHAMPAGNE
    "FR44ZAG10": (48.1161, 5.1410),   # ZAG LANGRES

    # Île-de-France
    "FR11ZAS01": (48.8566, 2.3522),   # ZAS PARIS
    "FR11ZAS02": (48.9355, 2.3580),   # ZAS SEINE-SAINT-DENIS
    "FR11ZAS03": (48.8146, 2.3940),   # ZAS VAL-DE-MARNE
    "FR11ZAS04": (48.8966, 2.1330),   # ZAS HAUTS-DE-SEINE

    # Hauts-de-France
    "FR32ZAH01": (50.6292, 3.0573),   # ZAH LILLE
    "FR32ZAH02": (50.2833, 2.7833),   # ZAH ARRAS
    "FR32ZAH03": (50.6942, 1.6133),   # ZAH BOULOGNE-SUR-MER
    "FR32ZAH04": (49.8939, 2.3000),   # ZAH AMIENS

    # Normandie
    "FR28ZAN01": (49.4431, 1.0993),   # ZAN ROUEN
    "FR28ZAN02": (49.1829, -0.3707),  # ZAN CAEN
    "FR28ZAN03": (48.7600, 1.9300),   # ZAN ÉVREUX

    # Bretagne
    "FR53ZAB01": (48.1173, -1.6778),  # ZAB RENNES
    "FR53ZAB02": (47.9950, -4.0970),  # ZAB QUIMPER
    "FR53ZAB03": (48.3904, -4.4861),  # ZAB BREST

    # Pays de la Loire
    "FR52ZAP01": (47.2184, -1.5536),  # ZAP NANTES
    "FR52ZAP02": (47.4736, -0.5516),  # ZAP ANGERS
    "FR52ZAP03": (47.9961, 0.1969),   # ZAP LE MANS

    # Centre-Val de Loire
    "FR24ZAC01": (47.9029, 1.9093),   # ZAC ORLÉANS
    "FR24ZAC02": (47.3900, 0.6889),   # ZAC TOURS
    "FR24ZAC03": (47.0820, 2.3960),   # ZAC BOURGES

    # Nouvelle-Aquitaine
    "FR75ZAA01": (44.8378, -0.5792),  # ZAA BORDEAUX
    "FR75ZAA02": (43.7000, -1.0833),  # ZAA BAYONNE
    "FR75ZAA03": (45.8336, 1.2611),   # ZAA LIMOGES
    "FR75ZAA04": (45.1833, 0.7167),   # ZAA PÉRIGUEUX

    # Occitanie
    "FR76ZAO01": (43.6047, 1.4442),   # ZAO TOULOUSE
    "FR76ZAO02": (43.6108, 3.8767),   # ZAO MONTPELLIER
    "FR76ZAO03": (43.2150, 2.3510),   # ZAO CARCASSONNE

    # Auvergne-Rhône-Alpes
    "FR84ZAR01": (45.7640, 4.8357),   # ZAR LYON
    "FR84ZAR02": (45.1885, 5.7245),   # ZAR GRENOBLE
    "FR84ZAR03": (45.8992, 6.1294),   # ZAR ANNECY
    "FR84ZAR04": (45.7788, 3.0873),   # ZAR CLERMONT-FERRAND

    # Provence-Alpes-Côte d’Azur
    "FR93ZAP01": (43.2965, 5.3698),   # ZAP MARSEILLE
    "FR93ZAP02": (43.7034, 7.2663),   # ZAP NICE
    "FR93ZAP03": (43.5297, 5.4474),   # ZAP AIX-EN-PROVENCE
    "FR93ZAP04": (43.1250, 5.9300),   # ZAP TOULON
}


df_clean["lat"] = df_clean["code_zas"].map(lambda c: ZAS_COORDS.get(str(c), (None, None))[0])
df_clean["lon"] = df_clean["code_zas"].map(lambda c: ZAS_COORDS.get(str(c), (None, None))[1])


n_geo = df_clean[["lat", "lon"]].notna().all(axis=1).sum()
print(f"Coordonnées ZAS ajoutées : {n_geo} lignes géolocalisées.")



print("Sauvegarde en Parquet...")
save_parquet(df_clean)

print("Terminé : data/processed/air_quality.parquet")
