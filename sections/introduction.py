# sections/introduction.py
import streamlit as st
import pandas as pd

def render(df):
    st.title("Un lundi sous surveillance : comprendre l’air que nous respirons")
    st.caption("Projet EFREI Paris — Module Data Analysis & Visualization")

    st.markdown("""
Chaque **lundi matin**, des millions de Français reprennent le travail, les routes se remplissent et les villes s’animent.  
Mais **que se passe-t-il dans l’air que nous respirons à ce moment précis ?**

En étudiant les données de qualité de l’air du **premier lundi d’août et de septembre**, pour **2024 et 2025**,  
nous explorons une photographie représentative des **cycles d’activité humaine** — entre le **calme estival** et la **reprise**.
    """)

    st.divider()

    st.subheader("Contexte et source des données")
    st.markdown("""
La surveillance de la qualité de l’air en France est assurée par les **AASQA** (Associations Agréées de Surveillance de la Qualité de l’Air),
sous la coordination du **LCSQA**. Les données sont centralisées dans la base **Geod’air** et publiées sur **data.gouv.fr**.

Le jeu de données provient du **flux E2 (“Up-To-Date”)**, qui regroupe en **temps réel** les mesures horaires des polluants réglementés :
- **NO₂** : dioxyde d’azote (trafic)
- **O₃** : ozone
- **SO₂** : dioxyde de soufre
- **CO** : monoxyde de carbone
- **PM10 / PM2.5** : particules fines

Jours étudiés : **5 août 2024**, **2 septembre 2024**, **4 août 2025**, **1er septembre 2025**.
    """)

    try:
        has_o3_2025 = (
            "annee" in df.columns and "pollutant" in df.columns and
            (df.query("annee == 2025 and pollutant == 'O3'").shape[0] > 0)
        )
    except Exception:
        has_o3_2025 = False

    if not has_o3_2025:
        st.warning(" **Disponibilité des données** : aucune mesure d’**ozone (O₃)** n’a été trouvée pour **2025** "
                   "dans les jours étudiés. Les comparaisons interannuelles utilisent donc principalement **NO₂**.")

    st.divider()

    st.subheader(" Problématique")
    st.markdown("""
- Les **activités humaines** influencent-elles la qualité de l’air entre la période **estivale** et la **rentrée** ?
    """)

    st.divider()

    st.subheader(" Informations du jeu de données (après nettoyage)")
    st.markdown("""
Chaque ligne représente **une mesure horaire** d’un polluant pour une station donnée. Colonnes principales utilisées :
- **date_heure** (datetime) → permet de dériver **annee / mois / jour / heure**
- **pollutant** (catégoriel) → NO₂, O₃, PM10, PM2.5, …
- **value** (numérique) → concentration (µg/m³ pour gaz/particules)
- **station_code** / **station_name** → station de mesure
- (colonnes techniques inutiles supprimées au nettoyage)
    """)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Lignes", f"{len(df):,}")
    c2.metric("Jours", int(df["jour"].nunique()) if "jour" in df.columns else "—")
    c3.metric("Polluants", int(df["pollutant"].nunique()) if "pollutant" in df.columns else "—")
    c4.metric("Stations", int(df["station_code"].nunique()) if "station_code" in df.columns else "—")

    st.divider()

    st.subheader("Carte des stations (aperçu)")
    lat_candidates = [c for c in df.columns if c in ["lat", "latitude", "lat_site", "latitude_site"]]
    lon_candidates = [c for c in df.columns if c in ["lon", "longitude", "lon_site", "longitude_site"]]

    if lat_candidates and lon_candidates:
        lat_col = lat_candidates[0]
        lon_col = lon_candidates[0]

        df_geo = df.copy()
        if {"station_code", "date_heure"}.issubset(df_geo.columns):
            df_geo = df_geo.sort_values("date_heure").groupby("station_code", as_index=False).tail(1)

        df_geo = df_geo.rename(columns={lat_col: "lat", lon_col: "lon"})
        try:
            df_geo["lat"] = pd.to_numeric(df_geo["lat"], errors="coerce")
            df_geo["lon"] = pd.to_numeric(df_geo["lon"], errors="coerce")
        except Exception:
            pass
        df_geo = df_geo.dropna(subset=["lat", "lon"])

        if not df_geo.empty:
            st.map(df_geo[["lat", "lon"]])
        else:
            st.info("Aucune coordonnée exploitable après nettoyage.")
    else:
        st.info("Pas de colonnes géographiques détectées (lat/lon). "
                "Pour afficher la carte, enrichir les données avec les coordonnées des stations.")

    st.divider()

    st.subheader("Aperçu des données")
    st.dataframe(df.head(100), use_container_width=True)

    st.caption("Source : LCSQA / Geod’air — Données temps réel (flux E2) — Licence Ouverte v2.0.")
