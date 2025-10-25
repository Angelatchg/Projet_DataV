# utils/prep.py
import pandas as pd
import re, unicodedata

def _norm(s):
    """Normalise un nom de colonne : minuscules, sans accents, espaces → underscore."""
    s = unicodedata.normalize("NFKD", s.strip().lower())
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    return re.sub(r"[^a-z0-9]+", "_", s).strip("_")

def clean_data(df):
    df = df.copy()
    df.columns = [_norm(c) for c in df.columns]

    mapping = {
        "date_de_debut": "date_heure",
        "date_de_fin": "date_fin",
        "polluant": "pollutant",
        "valeur": "value",
        "valeur_brute": "value_raw",
        "unite_de_mesure": "unit",
        "code_site": "station_code",
        "nom_site": "station_name",
        "code_qualite": "quality_code",
        "validite": "validity",
        "type_d_implantation": "implantation_type",
        "type_d_influence": "influence_type",
        "reglementaire": "reglementaire",
        "procedure_de_mesure": "procedure_mesure",
        "type_de_valeur": "value_type",
        "taux_de_saisie": "taux_saisie",
        "couverture_temporelle": "coverage_time",
        "couverture_de_donnees": "coverage_data",
        "organisme": "organisme",
        "code_zas": "code_zas",
        "zas": "zas",
        "discriminant": "discriminant",
    }
    df = df.rename(columns={k: v for k, v in mapping.items() if k in df.columns})

    if "date_heure" not in df.columns:
        if "date_fin" in df.columns:
            df["date_heure"] = df["date_fin"]
        else:
            raise KeyError("Impossible de trouver une colonne date (ni 'Date de début' ni 'Date de fin').")

    dt = pd.to_datetime(df["date_heure"], errors="coerce", format="%Y/%m/%d %H:%M:%S")
    if dt.isna().any():
        mask = dt.isna()
        dt.loc[mask] = pd.to_datetime(df.loc[mask, "date_heure"], errors="coerce")
    df["date_heure"] = dt

    if "value" in df.columns:
        df["value"] = pd.to_numeric(df["value"], errors="coerce")
    if "validity" in df.columns:
        df = df[df["validity"] == 1]

    df = df.dropna(subset=["date_heure", "value", "pollutant"])

    df["annee"] = df["date_heure"].dt.year
    df["mois"]  = df["date_heure"].dt.month
    df["jour"]  = df["date_heure"].dt.date
    df["heure"] = df["date_heure"].dt.hour

    df["pollutant"] = df["pollutant"].astype(str).str.upper().str.strip()

    cols_to_drop = [
        "reglementaire", "validity", "discriminant",
        "taux_saisie", "coverage_time", "coverage_data",
    ]
    df = df.drop(columns=[c for c in cols_to_drop if c in df.columns], errors="ignore")

    return df

def make_tables(df):
    tables: dict = {}

    tables["kpis"] = {
        "nb_rows": int(len(df)),
        "nb_days": int(df["jour"].nunique()) if "jour" in df.columns else None,
        "nb_stations": int(df["station_code"].nunique()) if "station_code" in df.columns else None,
        "mean": float(df["value"].mean()) if "value" in df.columns else None,
        "max": float(df["value"].max()) if "value" in df.columns else None,
    }

    if {"annee", "heure", "pollutant", "value"}.issubset(df.columns):
        tables["hourly"] = (
            df.groupby(["annee", "heure", "pollutant"], as_index=False)["value"]
              .agg(mean="mean", max="max")
        )
    else:
        tables["hourly"] = pd.DataFrame()

    if {"annee", "pollutant", "value"}.issubset(df.columns):
        tables["year_avg"] = (
            df.groupby(["annee", "pollutant"], as_index=False)["value"]
              .mean()
              .rename(columns={"value": "moyenne"})
        )
    else:
        tables["year_avg"] = pd.DataFrame()

    if {"mois", "annee", "pollutant", "value"}.issubset(df.columns):
        month_map = {8: "Août", 9: "Septembre"}
        d = df[df["mois"].isin([8, 9])].copy()
        d["mois_label"] = d["mois"].map(month_map).fillna(d["mois"].astype(str))
        tables["month_avg"] = (
            d.groupby(["annee", "mois_label", "pollutant"], as_index=False)["value"]
             .mean()
             .rename(columns={"value": "moyenne"})
        )
    else:
        tables["month_avg"] = pd.DataFrame()

    return tables
