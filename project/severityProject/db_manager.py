# db_manager.py
import pandas as pd
from tabulate import tabulate
import papermill

class ReportDataManager:
    def __init__(self, lang="fr", id_report="HOSP_001"):
        self.lang = lang
        self.id_report = id_report
        self.df_labels = self._load_labels_database()

    def _load_labels_database(self):
        # À remplacer par votre connexion réelle (ex: pd.read_sql("SELECT * FROM labels", conn))
        db_labels = [
            {"id_report": "HOSP_001", "nom_label": "titre_section_1", "txt_fr": "Identification de l'envoi", "txt_nl": "Sending Identificatie"},
            {"id_report": "HOSP_001", "nom_label": "titre_section_2", "txt_fr": "Suivi des Erreurs", "txt_nl": "Opvolging van Fouten"},
            {"id_report": "HOSP_001", "nom_label": "intro_p2", "txt_fr": "Anomalies triées par niveau de criticité.", "txt_nl": "Anomalieën gesorteerd op kriticititeitsniveau."},
            {"id_report": "HOSP_001", "nom_label": "th1_param", "txt_fr": "Paramètre", "txt_nl": "Parameter"},
            {"id_report": "HOSP_001", "nom_label": "th1_val", "txt_fr": "Valeurs extraites", "txt_nl": "Geëxtraheerde waarden"},
            {"id_report": "HOSP_001", "nom_label": "th2_sev", "txt_fr": "Sévérité", "txt_nl": "Ernstgraad"},
            {"id_report": "HOSP_001", "nom_label": "th2_code", "txt_fr": "Code Erreur / Total", "txt_nl": "Foutcode / Totaal"},
            {"id_report": "HOSP_001", "nom_label": "th2_desc", "txt_fr": "Description", "txt_nl": "Beschrijving"},
            {"id_report": "HOSP_001", "nom_label": "th2_nb", "txt_fr": "Nb d'erreur", "txt_nl": "Aantal fouten"},
            {"id_report": "HOSP_001", "nom_label": "lbl_severite", "txt_fr": "Sévérité", "txt_nl": "Ernstgraad"},
            {"id_report": "HOSP_001", "nom_label": "total_severite", "txt_fr": "Total Sévérité {sev} =", "txt_nl": "Totaal Ernstgraad {sev} ="},
            {"id_report": "HOSP_001", "nom_label": "total_general", "txt_fr": "Total Général =", "txt_nl": "Algemeen Totaal ="},
            {"id_report": "HOSP_001", "nom_label": "hosp_nom", "txt_fr": "Nom de l'hôpital", "txt_nl": "Naam van het ziekenhuis"},
            {"id_report": "HOSP_001", "nom_label": "hosp_annee", "txt_fr": "Année", "txt_nl": "Jaar"},
            {"id_report": "HOSP_001", "nom_label": "hosp_periode", "txt_fr": "Période", "txt_nl": "Periode"},
            {"id_report": "HOSP_001", "nom_label": "sev1_title", "txt_fr": "Severity 1 = Erreur bloquante.", "txt_nl": "Severity 1 = Blokkerende fout."},
            {"id_report": "HOSP_001", "nom_label": "sev1_desc", "txt_fr": "Les erreurs bloquantes sont des erreurs fatales et doivent absolument être corrigées avant de pouvoir aller plus loin.", "txt_nl": "Blokkerende fouten zijn fatale fouten en moeten absoluut worden gecorrigeerd voordat verder kan worden gegaan."},

            {"id_report": "HOSP_001", "nom_label": "sev2_title", "txt_fr": "Severity 2 = Erreur non bloquante.", "txt_nl": "Severity 2 = Niet-blokkerende fout."},
            {"id_report": "HOSP_001", "nom_label": "sev2_desc", "txt_fr": "Les erreurs non bloquantes doivent être vérifiées et contrôlées par rapport à la réalité. Si les données reflètent la situation réelle, elles ne doivent pas être modifiées. Dans le cas contraire, la modification est obligatoire.", "txt_nl": "Niet-blokkerende fouten moeten worden gecontroleerd en gevalideerd ten opzichte van de werkelijkheid. Als de gegevens correct zijn, hoeven ze niet te worden aangepast. In het andere geval is aanpassing verplicht."},

            {"id_report": "HOSP_001", "nom_label": "sev3_title", "txt_fr": "Severity 3 = Avertissement.", "txt_nl": "Severity 3 = Waarschuwing."},
            {"id_report": "HOSP_001", "nom_label": "sev3_desc", "txt_fr": "Les erreurs de sévérité 3 attirent l'attention sur des valeurs de champ qui pourraient être incorrectes. Une correction des données n'est pas nécessairement obligatoire, puisqu'il s'agit d'avertissements.", "txt_nl": "Fouten van niveau 3 vestigen de aandacht op mogelijke afwijkingen in gegevens. Correctie is niet noodzakelijk verplicht, aangezien het om waarschuwingen gaat."}
        ]
        return pd.DataFrame(db_labels)

    def get_txt(self, nom_label):
        col_lang = f"txt_{self.lang}"
        filtre = (self.df_labels["id_report"] == self.id_report) & (self.df_labels["nom_label"] == nom_label)
        resultat = self.df_labels.loc[filtre, col_lang]
        return resultat.values[0] if not resultat.empty else f"[{nom_label}]"

    def get_hospital_data(self):
        # Simulation d'une requête SQL de données métiers
        return pd.DataFrame({
            "Information": [self.get_txt("hosp_nom"), self.get_txt("hosp_annee"), self.get_txt("hosp_periode")],
            "Valeur": ["CHR Namur", "2026", "Semestre 1"]
        })

    def get_errors_data(self):
        # Simulation d'une requête SQL d'erreurs
        return pd.DataFrame({
            "Severite": [1, 1, 2, 2, 3, 3],
            "Code_Erreur": ["ERR-101", "ERR-102", "ERR-201", "ERR-202", "ERR-301", "ERR-302"],
            "Description": ["Panne serveur", "Crash DB", "Timeout API", "Disque 80%", "Session exp.", "Lenteur"],
            "Nb_Erreur": [5, 2, 12, 4, 45, 8]
        })
