# pdf_components.py
import pandas as pd
from great_tables import GT, style, loc


def generate_hospital_table(df, db_manager):
    cells = []

    for _, row in df.iterrows():
        cells.append(f"[#align(right)[{row['Information']}]]")
        cells.append(f"[#align(left)[{row['Valeur']}]]")

    table = f"""#align(center)[
  #table(
    columns: (2fr, 2fr),
    column-gutter: 5pt,
    stroke: white,
    inset: (x: 4pt, y: 2pt),
    {" , ".join(cells)}
  )
]"""
    return table

def generate_severity_errors_table(df_err, db_manager):
    """Génère le tableau complexe avec Great Tables"""
    
    df_err = df_err.copy()
    df_err["Severite"] = pd.to_numeric(df_err["Severite"], errors="coerce").astype("Int64")
    df_err["Nb_Erreur"] = pd.to_numeric(df_err["Nb_Erreur"], errors="coerce").astype("Int64")

    totaux_par_sev = df_err.groupby("Severite")["Nb_Erreur"].sum().to_dict()
    total_general = int(df_err["Nb_Erreur"].sum())

    lbl_sev_prefixe = db_manager.get_txt("lbl_severite")
    lignes_finales = []

    for sev, groupe in df_err.groupby("Severite", sort=True):
        for _, row in groupe.iterrows():
            lignes_finales.append({
                "Sev_Num": int(row["Severite"]),
                "Severite": str(int(row["Severite"])),
                "Code_Erreur": row["Code_Erreur"],
                "Description": row["Description"],
                "Nb_Erreur": int(row["Nb_Erreur"]),
                "Type_Ligne": "Donnee"
            })

        # Sous-total : total dans la dernière colonne Nb_Erreur
        lignes_finales.append({
            "Sev_Num": int(sev),
            "Severite": f"Total {int(sev)}",
            "Code_Erreur": "",
            "Description": "",
            "Nb_Erreur": int(totaux_par_sev[sev]),
            "Type_Ligne": f"Sous-Total-{int(sev)}"
        })

    # Total général : total dans la dernière colonne Nb_Erreur
    lignes_finales.append({
        "Sev_Num": None,
        "Severite": db_manager.get_txt("total_general"),
        "Code_Erreur": "",
        "Description": "",
        "Nb_Erreur": total_general,
        "Type_Ligne": "Total-General"
    })

    df_final = pd.DataFrame(lignes_finales)

    # Index pour le styling
    idx_sev1 = df_final[(df_final["Type_Ligne"] == "Donnee") & (df_final["Sev_Num"] == 1)].index.tolist()
    idx_sev2 = df_final[(df_final["Type_Ligne"] == "Donnee") & (df_final["Sev_Num"] == 2)].index.tolist()
    idx_sev3 = df_final[(df_final["Type_Ligne"] == "Donnee") & (df_final["Sev_Num"] == 3)].index.tolist()

    idx_subtotals = df_final[df_final["Type_Ligne"].str.contains("Sous-Total")].index.tolist()
    idx_grand_total = df_final[df_final["Type_Ligne"] == "Total-General"].index.tolist()

    gt_table = (
        GT(df_final.drop(columns=["Type_Ligne", "Sev_Num"]))
        .cols_label(
            Severite=db_manager.get_txt("th2_sev"),
            Code_Erreur=db_manager.get_txt("th2_code"),
            Description=db_manager.get_txt("th2_desc"),
            Nb_Erreur=db_manager.get_txt("th2_nb")
        )
        .sub_missing(columns=["Description", "Code_Erreur"], missing_text="")
        .fmt_integer(columns="Nb_Erreur")
        .cols_align(align="right", columns="Nb_Erreur")
        .tab_style(
            style=[style.fill(color="#e74c3c"), style.text(color="white", weight="bold")],
            locations=loc.body(columns="Severite", rows=idx_sev1)
        )
        .tab_style(
            style=[style.fill(color="#e67e22"), style.text(color="white", weight="bold")],
            locations=loc.body(columns="Severite", rows=idx_sev2)
        )
        .tab_style(
            style=[style.fill(color="#2ecc71"), style.text(color="white", weight="bold")],
            locations=loc.body(columns="Severite", rows=idx_sev3)
        )
        .tab_style(
            style=[style.fill(color="#f4f6f7"), style.text(weight="bold")],
            locations=loc.body(rows=idx_subtotals)
        )
        .tab_style(
            style=[style.fill(color="#eaeded"), style.text(weight="bold")],
            locations=loc.body(rows=idx_grand_total)
        )
        # centrage du tableau
        .tab_options(
            table_margin_left="auto",
            table_margin_right="auto"
        )
    )

    return gt_table

def typst_escape(value):
    """Échappe les caractères sensibles pour Typst."""
    if value is None:
        return ""
    s = str(value)
    s = s.replace("\\", "\\\\")
    s = s.replace('"', '\\"')
    return s

def generate_severity_errors_table_typst(df_err, db_manager):
    """Génère le tableau des erreurs en Typst natif, centré, avec styles."""
    
    df_err = df_err.copy()
    df_err["Severite"] = pd.to_numeric(df_err["Severite"], errors="coerce").astype("Int64")
    df_err["Nb_Erreur"] = pd.to_numeric(df_err["Nb_Erreur"], errors="coerce").astype("Int64")

    totaux_par_sev = df_err.groupby("Severite")["Nb_Erreur"].sum().to_dict()
    total_general = int(df_err["Nb_Erreur"].sum())

    lignes = []

    for sev, groupe in df_err.groupby("Severite", sort=True):
        for _, row in groupe.iterrows():
            sev_num = int(row["Severite"])
            code = typst_escape(row["Code_Erreur"])
            desc = typst_escape(row["Description"])
            nb = int(row["Nb_Erreur"])

            # Couleur selon sévérité
            if sev_num == 1:
                sev_cell = f'[#rect(fill: rgb("#e74c3c"), inset: 4pt)[#text(fill: white, weight: "bold")[{sev_num}]]]'
            elif sev_num == 2:
                sev_cell = f'[#rect(fill: rgb("#e67e22"), inset: 4pt)[#text(fill: white, weight: "bold")[{sev_num}]]]'
            else:
                sev_cell = f'[#rect(fill: rgb("#2ecc71"), inset: 4pt)[#text(fill: white, weight: "bold")[{sev_num}]]]'

            lignes.append(
                f"""{sev_cell},
[#align(left)[{code}]],
[#align(left)[{desc}]],
[#align(right)[{nb}]]"""
            )

        # Ligne total par sévérité
        lignes.append(
            f'''[#text(weight: "bold")[Total {int(sev)}]],
[#text(weight: "bold")[]],
[#text(weight: "bold")[]],
[#align(right)[#text(weight: "bold")[{int(totaux_par_sev[sev])}]]]'''
        )

    # Total général
    lignes.append(
        f'''[#text(weight: "bold")[Total général]],
[#text(weight: "bold")[]],
[#text(weight: "bold")[]],
[#align(right)[#text(weight: "bold")[{total_general}]]]'''
    )

    th_sev = typst_escape(db_manager.get_txt("th2_sev"))
    th_code = typst_escape(db_manager.get_txt("th2_code"))
    th_desc = typst_escape(db_manager.get_txt("th2_desc"))
    th_nb = typst_escape(db_manager.get_txt("th2_nb"))

    table_typst = f"""
#align(center)[
  #table(
    columns: (1.2fr, 2fr, 4fr, 1.5fr),
    column-gutter: 0pt,
    inset: (x: 6pt, y: 4pt),
    stroke: 0.5pt + rgb("#bdc3c7"),

    [#text(weight: "bold")[{th_sev}]],
    [#text(weight: "bold")[{th_code}]],
    [#text(weight: "bold")[{th_desc}]],
    [#align(right)[#text(weight: "bold")[{th_nb}]]],

    {",\n\n    ".join(lignes)}
  )
]
"""
    return table_typst