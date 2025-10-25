# utils/io.py
from pathlib import Path
import pandas as pd

def load_from_list(paths):
    """Charge et concatène une liste explicite de fichiers CSV (séparateur ;)"""
    dfs = []
    for p in paths:
        p = Path(p)
        if not p.exists():
            raise FileNotFoundError(f"Fichier introuvable: {p}")
        df = pd.read_csv(p, sep=";", low_memory=False)
        df["source_file"] = p.name
        dfs.append(df)
    return pd.concat(dfs, ignore_index=True)

def save_parquet(df, path="data/processed/air_quality.parquet"):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path, index=False)
    print(f" Données enregistrées dans {path}")


