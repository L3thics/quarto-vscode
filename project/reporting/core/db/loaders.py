import pandas as pd

def load_labels_from_csv(path: str, rapport_id: int) -> dict:
    """Charge les libellés depuis CSV et retourne un dict indexé par 'var'"""
    df = pd.read_csv(path, sep=";", dtype=str)
    
    # 1. Convertir la colonne rapport_id en int pour comparaison
    df["rapport_id"] = pd.to_numeric(df["rapport_id"], errors="coerce").fillna(0).astype(int)
    
    # 2. Filtrer par rapport
    df = df[df["rapport_id"] == rapport_id]
    
    # 3. Sécurisation
    df = df.fillna("")
    
    # 4. Transformer en dict
    labels = {
        row["var"]: {
            "fr": row["frans"],
            "nl": row["nederlands"]
        }
        for _, row in df.iterrows()
    }
    return labels

#labels = load_labels_from_csv(path="data/labels.csv", rapport_id=42)
#print(labels["labelctrl"])
