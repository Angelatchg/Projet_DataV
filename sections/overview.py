# sections/overview.py
import streamlit as st
import pandas as pd
from utils.prep import make_tables
from utils.viz import line_chart, bar_chart


# Filtres
def sidebar_filters(df):
    st.sidebar.markdown("### Filtres")

    polluants = sorted(df["pollutant"].dropna().unique().tolist()) if "pollutant" in df.columns else []
    pollutant = st.sidebar.selectbox("Polluant", polluants if polluants else ["—"])

    years = sorted(df["annee"].dropna().unique().tolist()) if "annee" in df.columns else []
    y24 = 2024 in years and st.sidebar.checkbox("2024", value=True)
    y25 = 2025 in years and st.sidebar.checkbox("2025", value=True)
    years_sel = [y for y, chosen in [(2024, y24), (2025, y25)] if chosen]
    if not years_sel and years:
        years_sel = years

    month_mode = st.sidebar.radio(
        "Mois",
        options=["Août & Septembre", "Août", "Septembre"],
        index=0
    )
    if month_mode == "Août":
        months_sel = [8]
    elif month_mode == "Septembre":
        months_sel = [9]
    else:
        months_sel = [8, 9]

    hour_min, hour_max = st.sidebar.slider(
        "Plage horaire (0–23)",
        min_value=0, max_value=23, value=(0, 23)
    )

    metric = st.sidebar.selectbox("Métrique", ["moyenne horaire", "max horaire"], index=0)
    agg = "mean" if metric == "moyenne horaire" else "max"


    df_f = df.copy()
    if polluants:
        df_f = df_f[df_f["pollutant"] == pollutant]
    if years_sel and "annee" in df_f.columns:
        df_f = df_f[df_f["annee"].isin(years_sel)]
    if "mois" in df_f.columns:
        df_f = df_f[df_f["mois"].isin(months_sel)]
    if "heure" in df_f.columns:
        df_f = df_f[(df_f["heure"] >= hour_min) & (df_f["heure"] <= hour_max)]

    state = {
        "pollutant": pollutant,
        "years": years_sel,
        "months": months_sel,
        "hour_range": (hour_min, hour_max),
        "metric": metric,
        "agg": agg,
    }
    return df_f, state


# OVERVIEW
def render(df, state):
    st.title("Overview — Visualiser et comparer")
    st.caption("Tendances horaires, comparaison annuelle, variations Août/Sep.")

    if df.empty:
        st.warning("Aucune donnée pour ces filtres.")
        return

    tables = make_tables(df)

    k = tables["kpis"]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Lignes filtrées", f"{k['nb_rows']:,}")
    c2.metric("Stations", k["nb_stations"] if k["nb_stations"] is not None else "—")
    c3.metric("Moyenne", f"{k['mean']:.1f}" if k["mean"] is not None else "—")
    c4.metric("Maximum", f"{k['max']:.1f}" if k["max"] is not None else "—")

    st.subheader("1) Analyse horaire — évolution au fil de la journée")
    hourly = tables["hourly"]
    col_to_plot = "mean" if state["agg"] == "mean" else "max"
    hourly_p = (
        hourly[hourly["pollutant"] == state["pollutant"]]
        .rename(columns={col_to_plot: "value"})
        [["heure", "annee", "value"]]
        .dropna()
    )

    hourly_p = (
        hourly[hourly["pollutant"] == state["pollutant"]]
        .rename(columns={col_to_plot: "value"})
        [["heure", "annee", "value"]]
        .dropna()
    )
    hourly_p["annee"] = hourly_p["annee"].astype(str)   # <-- AJOUT
    line_chart(hourly_p, x="heure", y="value", color="annee", title="Profil journalier par année")

    st.subheader("2) Comparaison annuelle — 2024 vs 2025")
    year_avg = tables["year_avg"]
    year_avg_p = year_avg[year_avg["pollutant"] == state["pollutant"]][["annee", "moyenne"]]
    bar_chart(year_avg_p, x="annee", y="moyenne", title="Moyenne par année")

    st.subheader("3) Saison — Août vs Septembre")
    month_avg = tables["month_avg"]
    month_avg_p = month_avg[month_avg["pollutant"] == state["pollutant"]][["annee", "mois_label", "moyenne"]]
    bar_chart(month_avg_p, x="mois_label", y="moyenne", color="annee", title="Août vs Septembre")

    st.subheader("Qualité des données")
    missing = df["value"].isna().mean() if "value" in df.columns else 0.0
    duplicates = df.duplicated(subset=["date_heure", "station_code", "pollutant"]).sum() if {"date_heure","station_code","pollutant"}.issubset(df.columns) else 0
    st.write(f"- Taux de valeurs manquantes (value) : **{missing:.1%}**")
    st.write(f"- Doublons potentiels (date_heure, station, polluant) : **{duplicates}**")
