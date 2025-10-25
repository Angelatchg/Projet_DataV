# app.py
import streamlit as st
import pandas as pd

from sections.introduction import render as intro_render
from sections.overview import sidebar_filters as overview_filters, render as overview_render
from sections.deep_dives import sidebar_filters as deep_filters, render as deep_render
from sections.conclusions import render as conclu_render

st.set_page_config(page_title="Air Quality — Data Story", layout="wide")

DATA_PATH = "data/processed/air_quality.parquet"

@st.cache_data(show_spinner=False)
def load_data(path):
    """Charge le parquet une seule fois (cache)."""
    return pd.read_parquet(path)

try:
    df = load_data(DATA_PATH)
except FileNotFoundError:
    st.error(f"Fichier introuvable : {DATA_PATH}\n\n"
             "Lance d’abord : `python merge_data.py` pour créer la base.")
    st.stop()
except Exception as e:
    st.error(f"Impossible de lire {DATA_PATH}\n\nDétail : {e}")
    st.stop()

# Navigation
st.sidebar.header("Navigation")
page = st.sidebar.radio(
    "Aller à…",
    options=["Introduction", "Overview", "Deep-dives", "Conclusion"],
    index=0,
)


# Filtres 
filtered_df = df
filter_state = {}

if page == "Overview":
    filtered_df, filter_state = overview_filters(df) 
elif page == "Deep-dives":
    filtered_df, filter_state = deep_filters(df) 

if page == "Introduction":
    intro_render(df)

elif page == "Overview":
    overview_render(filtered_df, filter_state)

elif page == "Deep-dives":
    deep_render(filtered_df, filter_state)

elif page == "Conclusion":
    conclu_render()
