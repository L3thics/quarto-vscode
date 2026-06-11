# db_manager.py
import pandas as pd
from tabulate import tabulate
import papermill as pm
from core.db.loaders import load_labels_from_csv
from pathlib import Path

class ReportDataManager:

    def __init__(self, lang: str, id_report: str):
        self.lang = lang
        self.id_report = id_report

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
    

    def get_hospital_data(self):
        # Simulation d'une requête SQL de données métiers
        return pd.DataFrame({
            "Information": [self.get_txt("HosName"), self.get_txt("year"), self.get_txt("periode")],
            "Valeur": ["CHR Namur", "2026", "Semestre 1"]
        })

    def get_errors_data(self):
        # Simulation d'une requête SQL d'erreurs
        return pd.DataFrame({
            "Severite": [1, 1, 2, 2, 3, 3,4,4],
            "Code_Erreur": ["ERR-101", "ERR-102", "ERR-201", "ERR-202", "ERR-301", "ERR-302", "ERR-401", "ERR-402"],
            "Description": ["Panne serveur", "Crash DB", "Timeout API", "Disque 80%", "Session exp.", "Lenteur", "Mauvaise performance", "Erreur de configuration"],
            "Nb_Erreur": [5, 2, 12, 4, 45, 8, 3, 1]
        })


