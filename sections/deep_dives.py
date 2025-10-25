# sections/deep_dives.py
import streamlit as st
import pandas as pd
import altair as alt
from utils.viz import line_chart, bar_chart

THRESHOLDS = {"O3": 180, "NO2": 200, "PM10": 50, "PM2_5": 25, "SO2": 125} 

def _norm_pollutant_key(p):
    """Uniformise le libellé polluant pour lookup des seuils."""
    p = (p or "").upper().strip().replace(" ", "").replace("-", "")
    p = p.replace("PM2.5", "PM2_5").replace("PM25", "PM2_5")
    return p

# Filtres
def sidebar_filters(df):
    st.sidebar.markdown("### Filtres")

    pols = sorted(df["pollutant"].dropna().unique().tolist()) if "pollutant" in df.columns else []
    default_p1 = "O3" if "O3" in pols else (pols[0] if pols else "—")
    default_p2 = "NO2" if "NO2" in pols else (pols[1] if len(pols) > 1 else default_p1)

    p1 = st.sidebar.selectbox("Polluant A", pols if pols else ["—"],
                              index=(pols.index(default_p1) if default_p1 in pols else 0))
    pols_b = [p for p in pols if p != p1] if len(pols) > 1 else pols
    p2 = st.sidebar.selectbox("Polluant B", pols_b if pols_b else ["—"],
                              index=(pols_b.index(default_p2) if default_p2 in pols_b else 0))

    years = sorted(df["annee"].dropna().unique().tolist()) if "annee" in df.columns else []
    y24 = 2024 in years and st.sidebar.checkbox("2024", value=True)
    y25 = 2025 in years and st.sidebar.checkbox("2025", value=True)
    years_sel = [y for y, on in [(2024, y24), (2025, y25)] if on] or years

    month_mode = st.sidebar.radio("Mois", ["Août & Septembre", "Août", "Septembre"], index=0)
    months_sel = [8, 9] if month_mode == "Août & Septembre" else ([8] if month_mode == "Août" else [9])

    hour_min, hour_max = st.sidebar.slider("Plage horaire (0–23)", 0, 23, (0, 23))

    metric = st.sidebar.selectbox("Métrique (profil horaire)", ["moyenne horaire", "max horaire"], index=0)
    agg = "mean" if metric == "moyenne horaire" else "max"


    df_f = df.copy()
    if "annee" in df_f.columns:
        df_f = df_f[df_f["annee"].isin(years_sel)]
    if "mois" in df_f.columns:
        df_f = df_f[df_f["mois"].isin(months_sel)]
    if "heure" in df_f.columns:
        df_f = df_f[(df_f["heure"] >= hour_min) & (df_f["heure"] <= hour_max)]

    state = {
        "p1": p1,
        "p2": p2,
        "years": years_sel,
        "months": months_sel,
        "hour_range": (hour_min, hour_max),
        "metric": metric,
        "agg": agg,
    }
    return df_f, state


def _hourly_profile(df, agg):
    """Pivot (index=heure, colonnes=annee) pour un polluant donné."""
    if df.empty:
        return pd.DataFrame()
    g = (
        df.groupby(["annee", "heure"])["value"]
          .agg(agg).reset_index()
          .pivot(index="heure", columns="annee", values="value")
          .sort_index()
    )
    return g

def _exceedances(df, pollutant, years_sel=None):
    """Nombre d'heures > seuil par année. Vide si pas de seuil défini."""
    key = _norm_pollutant_key(pollutant)
    thr = THRESHOLDS.get(key)
    if thr is None:
        return pd.DataFrame(columns=["annee", "depassements", "seuil"])

    d = df[df["pollutant"].str.upper().isin([pollutant.upper(), key])]
    years = years_sel or (sorted(df["annee"].unique().tolist()) if "annee" in df.columns else [])

    if d.empty:
        return pd.DataFrame({"annee": years, "depassements": [0]*len(years), "seuil": [thr]*len(years)})

    d = d.copy()
    d["depasse"] = d["value"] > thr
    out = d.groupby("annee")["depasse"].sum().rename("depassements").reset_index()
    out = out.set_index("annee").reindex(years, fill_value=0).reset_index()
    out["seuil"] = thr
    return out


# Page Deep-dives
def render(df, state):
    st.title("Deep-dives — analyses ciblées")
    st.caption("Duel de polluants, corrélation et dépassements de seuils.")
    st.markdown("""Nous allons étudier ici le cas de NO2 et PM10 qui sont les polluants les plus représentatifs de l'activité humaine""")

    if df.empty:
        st.warning("Aucune donnée pour ces filtres.")
        return

    p1, p2, agg = state["p1"], state["p2"], state["agg"]
    if p1 == p2:
        others = [p for p in df["pollutant"].unique().tolist() if p != p1]
        if others:
            p2 = others[0]

    df_p1 = df[df["pollutant"] == p1]
    df_p2 = df[df["pollutant"] == p2]


    st.subheader(f"1) Comment {p1} et {p2} varient-ils au fil de la journée ?")
    col1, col2 = st.columns(2)
    for dff, pol, c in [(df_p1, p1, col1), (df_p2, p2, col2)]:
        with c:
            st.markdown(f"**{pol} — {state['metric']} par heure (par année)**")
            g = _hourly_profile(dff, agg)
            if g.empty:
                st.info(f"Aucune donnée pour {pol}.")
            else:
                tidy = g.reset_index().melt(id_vars="heure", var_name="annee", value_name="value")
                tidy["annee"] = tidy["annee"].astype(str)
                line_chart(tidy, x="heure", y="value", color="annee", title=f"Profil {pol}")
    st.markdown("**Août — période estivale**") 
    st.markdown("Les concentrations de NO₂ se situent globalement entre 5 et 15 µg/m³, et celles de PM10 autour de 10 à 14 µg/m³." \
    "\n La dispersion importante des points montre une corrélation faible entre les deux polluants : lorsque le NO₂ augmente, le PM10 ne suit pas toujours la même tendance.\n" \
    "\n Cette indépendance traduit des conditions de dispersion atmosphérique favorables (ensoleillement, vent) et une réduction du trafic routier pendant les vacances.")
    st.markdown("\n**Septembre — période de reprise**")
    st.markdown("Les pics horaires deviennent beaucoup plus nets pour les deux polluants :" \
    "\nLe pic du matin de NO₂ (vers 6–8h) est plus élevé, atteignant jusqu’à 18–20 µg/m³, traduisant la reprise du trafic routier." \
    "\nLes particules PM10 suivent la même tendance, avec un pic matinal coïncidant, et des valeurs plus élevées sur toute la journée." \
    "\nLe pic du soir (vers 19–21h) reste visible, mais moins marqué qu’en matinée." \
    "\nLes pics horaires sont synchrones avec les heures de pointe de la journée, confirmant que le trafic routier est le principal moteur de la pollution observée.")
    st.markdown("En comparant les profils horaires d’août et de septembre, on constate une hausse significative des concentrations de NO₂ et de PM10 à la rentrée. Les deux polluants partagent des pics synchrones, preuve que le trafic routier influence directement leur évolution. Ce comportement valide l’hypothèse d’un “effet rentrée” sur la qualité de l’air, avec un impact plus marqué sur le NO₂, indicateur direct du trafic automobile." \
    "\nCependant cette pollution à diminuer en 1 ans. Cela suit fortement les mentalités actuellement qui consiste à moins conduire et a priorisé les transports plus écologique.")

    st.subheader(f"2) Comment {p1} et {p2} évoluent-ils ensemble ?")
    if {"date_heure", "pollutant", "value", "annee"}.issubset(df.columns):
        pivot = (
            df[df["pollutant"].isin([p1, p2])]
            .pivot_table(index=["date_heure", "annee"], columns="pollutant", values="value", aggfunc="mean")
            .reset_index()
        )

        for col in [p1, p2]:
            if col not in pivot.columns:
                pivot[col] = pd.NA

        pivot = pivot.dropna(subset=[p1, p2], how="any")

        if not pivot.empty:
            chart = (
                alt.Chart(pivot).mark_circle(size=60)
                .encode(
                    x=alt.X(p1, title=p1),
                    y=alt.Y(p2, title=p2),
                    color=alt.Color("annee:N", title="Année"),
                    tooltip=["date_heure:T", "annee:N", alt.Tooltip(p1, format=".1f"), alt.Tooltip(p2, format=".1f")],
                )
                .properties(height=350)
            )
            st.altair_chart(chart, use_container_width=True)
        else:
            st.info("Pas assez de points communs pour tracer la corrélation avec les filtres actuels (données manquantes pour l’un des deux polluants).")
    else:
        st.info("Colonnes nécessaires manquantes pour le scatter.")
    st.markdown("**Août — période estivale**" \
    "\n Les concentrations de NO₂ se situent globalement entre 5 et 15 µg/m³, et celles de PM10 autour de 10 à 14 µg/m³. " \
    "La dispersion importante des points montre une corrélation faible entre les deux polluants : lorsque le NO₂ augmente, le PM10 ne suit pas toujours la même tendance.")
    st.markdown("**Septembre — reprise d’activité** ")
    st.markdown("Les concentrations augmentent pour les deux polluants : NO₂ atteint des valeurs proches de 20 µg/m³, PM10 monte jusqu’à 16 µg/m³. " \
    "Les points se répartissent selon une diagonale montante, indiquant une corrélation positive forte entre NO₂ et PM10." \
    "Cela montre que lorsque le trafic reprend, les émissions de NO₂ (gaz d’échappement) et les particules (PM10) augmentent simultanément.")
    st.markdown("En août, les polluants évoluent indépendamment : l’activité humaine étant réduite, les émissions sont faibles et dispersées.\n En septembre, la corrélation se renforce : plus le trafic augmente, plus les niveaux de particules et de NO₂ montent ensemble. \n Cette tendance met en évidence un effet saisonnier anthropique, lié aux comportements humains (retour au travail, transport scolaire, chauffage léger).")

    st.subheader("3) Observe-t-on des dépassements de seuils de pollution selon les années ?")
    c1, c2 = st.columns(2)
    for col, pol in [(c1, p1), (c2, p2)]:
        ex = _exceedances(df, pol, years_sel=state["years"])
        with col:
            if ex.empty:
                st.info(f"Pas de seuil indicatif pour **{pol}**.")
                continue
            bar_chart(ex, x="annee", y="depassements", title=f"Dépassements — {pol}")
            if ex["depassements"].sum() == 0:
                st.caption("Aucun dépassement observé avec les filtres actuels.")
    st.markdown("Les dépassements de seuils correspondent au nombre d’heures où la concentration d’un polluant dépasse le seuil réglementaire fixé par les autorités sanitaires. Ils permettent d’évaluer l’intensité des épisodes de pollution et de comparer les années entre elles." \
    "\nSeuils de référence :  " \
    "\n- PM10 → 50 µg/m³ (valeur indicative journalière)  " \
    "\n- NO₂ → 200 µg/m³ (valeur horaire indicative)")
    st.markdown("L’analyse des dépassements de seuils confirme la dynamique observée dans les profils horaires :  \nUne pollution modérée et stable en été (août).  \nUne hausse marquée à la rentrée (septembre), principalement liée aux particules PM10.  " \
                "\nCes résultats soulignent que les particules fines constituent un indicateur sensible de l’intensité des activités humaines et qu’elles traduisent bien l’impact direct de la reprise urbaine sur la qualité de l’air.")