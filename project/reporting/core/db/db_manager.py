# db_manager.py
import os
import pandas as pd
import numpy as np
from tabulate import tabulate
from core.db.loaders import load_labels_from_csv
from pathlib import Path
import papermill as pm



# =====================================================================
# 1. LE DÉCORATEUR (Placé au niveau global du module)
# =====================================================================
def dump_dataframe(nom_etape):
    """Décorateur pour dumper automatiquement les DataFrames au format Parquet pour Data Wrangler."""

    def decorateur(fonction):
        def wrapper(self, *args, **kwargs):
            # 1. On cherche si un paramètre 'mode' a été passé à la méthode,
            # ou s'il est défini dans l'objet lui-même (self.mode)
            mode = kwargs.get("mode", getattr(self, "mode", "production"))

            # 2. On exécute la méthode de l'objet normalement
            resultat = fonction(self, *args, **kwargs)

            # 3. Si on est en debug et que c'est un DataFrame, on fait le dump au format Parquet
            if mode == "debug" and isinstance(resultat, pd.DataFrame):
                os.makedirs("./debug_dumps", exist_ok=True)
                # Utilisation de l'extension .parquet pour l'ouverture en un clic dans VS Code
                chemin = f"./debug_dumps/rep_{self.id_report}_{nom_etape}.parquet"

                # Sauvegarde au format Parquet (utilise pyarrow par défaut)
                resultat.to_parquet(chemin, index=True)
                print(f"💾 [DEBUG] Table dumpée (Parquet) : {chemin}")

            return resultat

        return wrapper

    return decorateur

class ReportDataManager:

    def __init__(self, lang: str, id_report: int, mode: str = "production"):
        self.lang = lang
        self.id_report = id_report
        self.mode = mode

        # ✅ trouver automatiquement la racine projet (reporting/)
        project_root = Path(__file__).resolve()

        while not (project_root / "data").exists():
            project_root = project_root.parent

        labels_path = project_root / "data" / "labels.csv"

        # ✅ debug optionnel
        #print("LABELS PATH =", labels_path)

        self.labels = load_labels_from_csv(
            path=str(labels_path),
            rapport_id=id_report
        )


    def get_txt(self, key: str) -> str:
        return self.labels.get(key, {}).get(self.lang, f"[{key}]")
    
    @dump_dataframe("hospital_data")
    def get_hospital_data(self):
        # Simulation d'une requête SQL de données métiers
        return pd.DataFrame({
            "Information": [self.get_txt("HosName"), self.get_txt("year"), self.get_txt("periode")],
            "Valeur": ["CHR Namur", "2026", "Semestre 1"]
        })

    @dump_dataframe("errors_data")
    def get_errors_data(self):
        # Simulation d'une requête SQL d'erreurs
        return pd.DataFrame({
            "Severite": [1, 1, 2, 2, 3, 3,4,4],
            "Code_Erreur": ["ERR-101", "ERR-102", "ERR-201", "ERR-202", "ERR-301", "ERR-302", "ERR-401", "ERR-402"],
            "Description": ["Panne serveur", "Crash DB", "Timeout API", "Disque 80%", "Session exp.", "Lenteur", "Mauvaise performance", "Erreur de configuration"],
            "Nb_Erreur": [5, 2, 12, 4, 45, 8, 3, 1]
        })

    @dump_dataframe("admission_data")
    def get_admission_data(self) -> pd.DataFrame:
        """
        Simule la table d'admissions. 
        À remplacer plus tard par une requête SQL Oracle.
        """
        np.random.seed(42)
        
        # Pool de diagnostics CIM-10
        diagnostics = [
            {"code_diag": "I21", "description": "Infarctus aigu du myocarde"},
            {"code_diag": "J44", "description": "Maladies pulmonaires obstructives chroniques"},
            {"code_diag": "E11", "description": "Diabète sucré de type 2"},
            {"code_diag": "N39", "description": "Autres affections de l'appareil urinaire"},
            {"code_diag": "A09", "description": "Gastro-entérite d'origine infectieuse"},
            {"code_diag": "F32", "description": "Épisodes dépressifs"},
            {"code_diag": "G30", "description": "Maladie d'Alzheimer"},
            {"code_diag": "I10", "description": "Hypertension essentielle (primitive)"},
            {"code_diag": "K52", "description": "Autres gastro-entérites non infectieuses"},
            {"code_diag": "M17", "description": "Gonarthrose [arthrose du genou]"},
            {"code_diag": "Z38", "description": "Enfants nés vivants selon le lieu"},
            {"code_diag": "C34", "description": "Tumeur maligne des bronches et du poumon"}
        ]
        
        types_hospi = ['H', 'F', 'M', 'L']
        
        # Création du produit cartésien (CIM-10 x Types)
        records = []
        for diag in diagnostics:
            for t in types_hospi:
                records.append({
                    "code_diag": diag["code_diag"],
                    "description": diag["description"],
                    "type_hospi": t,
                    "occurrences": np.random.randint(10, 500)
                })
                
        return pd.DataFrame(records)


