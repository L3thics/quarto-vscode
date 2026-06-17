import os
import pandas as pd

# =====================================================================
# 1. LE DÉCORATEUR (Placé au niveau global du module)
# =====================================================================
def dump_dataframe(nom_etape):
    """Décorateur pour dumper automatiquement les DataFrames des méthodes."""

    def decorateur(fonction):
        def wrapper(self, *args, **kwargs):
            # 1. On cherche si un paramètre 'mode' a été passé à la méthode,
            # ou s'il est défini dans l'objet lui-même (self.mode)
            mode = kwargs.get("mode", getattr(self, "mode", "production"))

            # 2. On exécute la méthode de l'objet normalement
            resultat = fonction(self, *args, **kwargs)

            # 3. Si on est en debug et que c'est un DataFrame, on fait le dump
            if mode == "debug" and isinstance(resultat, pd.DataFrame):
                os.makedirs("./debug_dumps", exist_ok=True)
                # On peut inclure l'id du rapport dans le nom du fichier pour s'y retrouver
                chemin = (
                    f"./debug_dumps/rep_{self.id_report}_{nom_etape}.pkl"
                )
                resultat.to_pickle(chemin)
                print(f"💾 [DEBUG] Table dumpée : {chemin}")

            return resultat

        return wrapper

    return decorateur