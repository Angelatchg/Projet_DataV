# utils/viz.py
import streamlit as st
import pandas as pd
import altair as alt

def _empty(df, cols):
    return df is None or df.empty or not set(cols).issubset(df.columns)

def line_chart(df, x, y, color = None, title = "", height = 320):
    if _empty(df, [x, y] + ([color] if color else [])):
        st.info("Pas assez de données pour la courbe.")
        return
    enc = {
        "x": alt.X(f"{x}:Q", title=x.replace("_", " ").title()),
        "y": alt.Y(f"{y}:Q", title=y.replace("_", " ").title()),
        "tooltip": [x, y] + ([color] if color else []),
    }

    if color:
        enc["color"] = alt.Color(f"{color}:N", title=color.replace("_", " ").title())
    chart = alt.Chart(df).mark_line(point=True).encode(**enc).properties(title=title, height=height)
    st.altair_chart(chart, use_container_width=True)

def bar_chart(df, x, y, color = None, title = "", height = 300):
    if _empty(df, [x, y] + ([color] if color else [])):
        st.info("Pas assez de données pour l’histogramme.")
        return
    enc = {
        "x": alt.X(f"{x}:O", title=x.replace("_", " ").title()),
        "y": alt.Y(f"{y}:Q", title=y.replace("_", " ").title()),
        "tooltip": [x, y],
    }
    if color:
        enc["color"] = alt.Color(color, title=color.replace("_", " ").title())
        enc["tooltip"].append(color)
    chart = alt.Chart(df).mark_bar().encode(**enc).properties(title=title, height=height)
    labels = chart.mark_text(dy=-6).encode(text=f"{y}:Q")
    st.altair_chart(chart + labels, use_container_width=True)
