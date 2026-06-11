# main.py
import core.db.db_manager as db_manager
def run_test():
    print("Démarrage du test...")
    report_manager = db_manager.ReportDataManager(lang="fr", id_report=42)
    print(report_manager.get_txt("labelctrl"))

if __name__ == "__main__":
    run_test()

