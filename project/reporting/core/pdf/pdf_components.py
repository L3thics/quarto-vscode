# pdf_components.py
import pandas as pd
from great_tables import GT, style, loc
from datetime import datetime

def generate_hospital_table(df, db_manager):
    cells = []

    # 1. Ajout des lignes dynamiques issues de la base de données hospitalière
    for _, row in df.iterrows():
        cells.append(f"[#align(right)[{row['Information']}]]")
        cells.append(f"[#align(left)[{row['Valeur']}]]")

    # 2. Récupération du label de la date et formatage de la date du jour (JJ/MM/AAAA)
    date_label = db_manager.get_txt("datelb") # Récupère par ex. "Date de génération" ou "Date"
    current_date = datetime.now().strftime("%d/%m/%Y")

    # 3. Injection de la ligne de date à la fin du tableau Typst
    cells.append(f"[#align(right)[{date_label}]]")
    cells.append(f"[#align(left)[{current_date}]]")

    # 4. Génération de la structure de la table Typst
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

    lbl_sev_prefixe = db_manager.get_txt("labelsev")
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
    idx_sev4 = df_final[(df_final["Type_Ligne"] == "Donnee") & (df_final["Sev_Num"] == 4)].index.tolist()

    idx_subtotals = df_final[df_final["Type_Ligne"].str.contains("Sous-Total")].index.tolist()
    idx_grand_total = df_final[df_final["Type_Ligne"] == "Total-General"].index.tolist()

    gt_table = (
        GT(df_final.drop(columns=["Type_Ligne", "Sev_Num"]))
        .cols_label(
            Severite=db_manager.get_txt("labelsev"),
            Code_Erreur=db_manager.get_txt("labelctrl"),
            Description=db_manager.get_txt("labeldesc"),
            Nb_Erreur=db_manager.get_txt("labelnb")
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
            style=[style.fill(color="#7bb2f5"), style.text(color="white", weight="bold")],
            locations=loc.body(columns="Severite", rows=idx_sev4)
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
                sev_cell = f'table.cell(fill: rgb("#e74c3c"))[#align(center)[#text(fill: white, weight: "bold")[{sev_num}]]]'
            elif sev_num == 2:
                sev_cell = f'table.cell(fill: rgb("#e67e22"))[#align(center)[#text(fill: white, weight: "bold")[{sev_num}]]]'
            elif sev_num == 3:
                sev_cell = f'table.cell(fill: rgb("#2ecc71"))[#align(center)[#text(fill: white, weight: "bold")[{sev_num}]]]'
            else:
                sev_cell = f'table.cell(fill: rgb("#7bb2f5"))[#align(center)[#text(fill: white, weight: "bold")[{sev_num}]]]'

            # if sev_num == 1:
            #     sev_cell = f'[#rect(fill: rgb("#e74c3c"), inset: 4pt)[#text(fill: white, weight: "bold")[{sev_num}]]]'
            # elif sev_num == 2:
            #     sev_cell = f'[#rect(fill: rgb("#e67e22"), inset: 4pt)[#text(fill: white, weight: "bold")[{sev_num}]]]'
            # elif sev_num == 3:
            #     sev_cell = f'[#rect(fill: rgb("#2ecc71"), inset: 4pt)[#text(fill: white, weight: "bold")[{sev_num}]]]'
            # else:
            #     sev_cell = f'[#rect(fill: rgb("#7bb2f5"), inset: 4pt)[#text(fill: white, weight: "bold")[{sev_num}]]]'

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
        f'''[#text(weight: "bold")[{db_manager.get_txt("total_general")}]],
[#text(weight: "bold")[]],
[#text(weight: "bold")[]],
[#align(right)[#text(weight: "bold")[{total_general}]]]'''
    )

    th_sev = typst_escape(db_manager.get_txt("labelsev"))
    th_code = typst_escape(db_manager.get_txt("labelctrl"))
    th_desc = typst_escape(db_manager.get_txt("labeldesc"))
    th_nb = typst_escape(db_manager.get_txt("labelnb"))

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


def make_text_cell(txt: str, align: str = "left", bold: bool = False) -> str:
    txt = typst_escape(str(txt))
    if bold:
        return f'#align({align})[#text(weight: "bold")[{txt}]]'
    return f'#align({align})[{txt}]'

def make_num_cell(value, bold: bool = False) -> str:
    if bold:
        return f'#align(right)[#text(weight: "bold")[{value}]]'
    return f'#align(right)[{value}]'

import pandas as pd


def generate_severity_errors_table_typst2(df_err, db_manager):
    """Génère un tableau Typst natif, propre et stylé pour les erreurs par sévérité."""

    df_err = df_err.copy()

    df_err["Severite"] = pd.to_numeric(df_err["Severite"], errors="coerce").astype("Int64")
    df_err["Nb_Erreur"] = pd.to_numeric(df_err["Nb_Erreur"], errors="coerce").astype("Int64")

    # On enlève les lignes invalides si besoin
    df_err = df_err.dropna(subset=["Severite", "Nb_Erreur", "Code_Erreur", "Description"])

    totaux_par_sev = df_err.groupby("Severite")["Nb_Erreur"].sum().to_dict()
    total_general = int(df_err["Nb_Erreur"].sum())

    # Labels traduits / échappés
    th_sev = typst_escape(db_manager.get_txt("labelsev"))
    th_code = typst_escape(db_manager.get_txt("labelctrl"))
    th_desc = typst_escape(db_manager.get_txt("labeldesc"))
    th_nb = typst_escape(db_manager.get_txt("labelnb"))
    txt_total_general = typst_escape(db_manager.get_txt("total_general"))

    def sev_color(sev_num: int) -> str:
        """Couleur de fond selon la sévérité."""
        colors = {
            1: '#d32f2f',   # rouge
            2: '#f57c00',   # orange
            3: '#388e3c',   # vert
            4: '#1976d2'    # bleu
        }
        return colors.get(sev_num, '#607d8b')  # gris bleuté par défaut

    def make_sev_cell(sev_num: int) -> str:
        """Cellule sévérité avec fond complètement coloré."""
        color = sev_color(sev_num)
        return (
            f'table.cell(fill: rgb("{color}"))'
            f'[#align(center)[#text(fill: white, weight: "bold")[{sev_num}]]]'
        )

    def make_text_cell(txt: str, align: str = "left", bold: bool = False) -> str:
        """Cellule texte simple."""
        txt = typst_escape(str(txt))
        if bold:
            return f'[#align({align})[#text(weight: "bold")[{txt}]]]'
        return f'[#align({align})[{txt}]]'

    def make_num_cell(value, bold: bool = False) -> str:
        """Cellule numérique alignée à droite."""
        if bold:
            return f'[#align(right)[#text(weight: "bold")[{value}]]]'
        return f'[#align(right)[{value}]]'

    lignes = []
    row_index = 0  # pour zebra rows

    for sev, groupe in df_err.groupby("Severite", sort=True):
        sev = int(sev)

        for _, row in groupe.iterrows():
            code = row["Code_Erreur"]
            desc = row["Description"]
            nb = int(row["Nb_Erreur"])

            # Zebra rows sur les 3 colonnes texte/nombre
            zebra_fill = 'rgb("#f7f9fb")' if row_index % 2 else 'white'

            ligne = f"""
{make_sev_cell(sev)},
table.cell(fill: {zebra_fill})[{make_text_cell(code, align="left")}],
table.cell(fill: {zebra_fill})[{make_text_cell(desc, align="left")}],
table.cell(fill: {zebra_fill})[{make_num_cell(nb)}]
""".strip()

            lignes.append(ligne)
            row_index += 1

        # Ligne total par sévérité
        lignes.append(
            f"""
table.cell(fill: rgb("#e9eef3"))[{make_text_cell(f"Total {sev}", align="center", bold=True)}],
table.cell(fill: rgb("#e9eef3"))[{make_text_cell("", bold=True)}],
table.cell(fill: rgb("#e9eef3"))[{make_text_cell("", bold=True)}],
table.cell(fill: rgb("#e9eef3"))[{make_num_cell(int(totaux_par_sev[sev]), bold=True)}]
""".strip()
        )

    # Total général
    lignes.append(
        f"""
table.cell(fill: rgb("#dbe5f1"))[{make_text_cell(txt_total_general, align="center", bold=True)}],
table.cell(fill: rgb("#dbe5f1"))[{make_text_cell("", bold=True)}],
table.cell(fill: rgb("#dbe5f1"))[{make_text_cell("", bold=True)}],
table.cell(fill: rgb("#dbe5f1"))[{make_num_cell(total_general, bold=True)}]
""".strip()
    )

    table_typst = f"""
#align(center)[
  #table(
    columns: (1.1fr, 2fr, 4.8fr, 1.4fr),
    inset: (x: 3pt, y: 1.5pt),
    column-gutter: 0pt,
    stroke: 0.6pt + rgb("#c7d0d9"),

    table.cell(fill: rgb("#1f4e79"))[#align(center)[#text(fill: white, weight: "bold")[{th_sev}]]],
    table.cell(fill: rgb("#1f4e79"))[#align(center)[#text(fill: white, weight: "bold")[{th_code}]]],
    table.cell(fill: rgb("#1f4e79"))[#align(center)[#text(fill: white, weight: "bold")[{th_desc}]]],
    table.cell(fill: rgb("#1f4e79"))[#align(center)[#text(fill: white, weight: "bold")[{th_nb}]]],

    {",\n\n    ".join(lignes)}
  )
]
""".strip()

    return table_typst

import pandas as pd


def generate_severity_errors_table_typst3(df_err, db_manager):
    """Génère un tableau Typst natif, compact et stylé pour les erreurs par sévérité."""

    df_err = df_err.copy()

    df_err["Severite"] = pd.to_numeric(df_err["Severite"], errors="coerce").astype("Int64")
    df_err["Nb_Erreur"] = pd.to_numeric(df_err["Nb_Erreur"], errors="coerce").astype("Int64")

    # On enlève les lignes invalides si besoin
    df_err = df_err.dropna(subset=["Severite", "Nb_Erreur", "Code_Erreur", "Description"])

    totaux_par_sev = df_err.groupby("Severite")["Nb_Erreur"].sum().to_dict()
    total_general = int(df_err["Nb_Erreur"].sum())

    # Labels traduits / échappés
    th_sev = typst_escape(db_manager.get_txt("labelsev"))
    th_code = typst_escape(db_manager.get_txt("labelctrl"))
    th_desc = typst_escape(db_manager.get_txt("labeldesc"))
    th_nb = typst_escape(db_manager.get_txt("labelnb"))
    txt_total_general = typst_escape(db_manager.get_txt("total_general"))

    def sev_color(sev_num: int) -> str:
        """Couleur de fond selon la sévérité."""
        colors = {
            1: '#d32f2f',   # rouge
            2: '#f57c00',   # orange
            3: '#388e3c',   # vert
            4: '#1976d2'    # bleu
        }
        return colors.get(sev_num, '#607d8b')  # gris bleuté par défaut

    def make_sev_cell(sev_num: int) -> str:
        """Cellule sévérité avec fond complètement coloré."""
        color = sev_color(sev_num)
        return (
            f'table.cell(fill: rgb("{color}"))'
            f'[#align(center)[#text(fill: white, weight: "bold")[{sev_num}]]]'
        )

    def make_text_cell(txt: str, align: str = "left", bold: bool = False) -> str:
        """Contenu de cellule texte (sans table.cell externe)."""
        txt = typst_escape(str(txt))
        if bold:
            return f'#align({align})[#text(weight: "bold")[{txt}]]'
        return f'#align({align})[{txt}]'

    def make_num_cell(value, bold: bool = False) -> str:
        """Contenu de cellule numérique aligné à droite (sans table.cell externe)."""
        if bold:
            return f'#align(right)[#text(weight: "bold")[{value}]]'
        return f'#align(right)[{value}]'

    lignes = []
    row_index = 0  # pour zebra rows

    for sev, groupe in df_err.groupby("Severite", sort=True):
        sev = int(sev)

        for _, row in groupe.iterrows():
            code = row["Code_Erreur"]
            desc = row["Description"]
            nb = int(row["Nb_Erreur"])

            # Zebra rows sur les 3 colonnes texte/nombre
            zebra_fill = 'rgb("#f7f9fb")' if row_index % 2 else 'white'

            ligne = f"""
{make_sev_cell(sev)},
table.cell(fill: {zebra_fill})[{make_text_cell(code, align="left")}],
table.cell(fill: {zebra_fill})[{make_text_cell(desc, align="left")}],
table.cell(fill: {zebra_fill})[{make_num_cell(nb)}]
""".strip()

            lignes.append(ligne)
            row_index += 1

        # Ligne total par sévérité
        lignes.append(
            f"""
table.cell(fill: rgb("#e9eef3"))[{make_text_cell(f"Total {sev}", align="center", bold=True)}],
table.cell(fill: rgb("#e9eef3"))[{make_text_cell("", bold=True)}],
table.cell(fill: rgb("#e9eef3"))[{make_text_cell("", bold=True)}],
table.cell(fill: rgb("#e9eef3"))[{make_num_cell(int(totaux_par_sev[sev]), bold=True)}]
""".strip()
        )

    # Total général
    lignes.append(
        f"""
table.cell(fill: rgb("#dbe5f1"))[{make_text_cell(txt_total_general, align="center", bold=True)}],
table.cell(fill: rgb("#dbe5f1"))[{make_text_cell("", bold=True)}],
table.cell(fill: rgb("#dbe5f1"))[{make_text_cell("", bold=True)}],
table.cell(fill: rgb("#dbe5f1"))[{make_num_cell(total_general, bold=True)}]
""".strip()
    )

    table_typst = f"""
#align(center)[
  #table(
    columns: (1.1fr, 2fr, 4.8fr, 1.4fr),
    inset: (x: 4pt, y: 3pt), // luxe inset: (x: 8pt, y: 6pt)
    column-gutter: 0pt,
    stroke: 0.6pt + rgb("#c7d0d9"),

    table.cell(fill: rgb("#1f4e79"))[#align(center)[#text(fill: white, weight: "bold")[{th_sev}]]],
    table.cell(fill: rgb("#1f4e79"))[#align(center)[#text(fill: white, weight: "bold")[{th_code}]]],
    table.cell(fill: rgb("#1f4e79"))[#align(center)[#text(fill: white, weight: "bold")[{th_desc}]]],
    table.cell(fill: rgb("#1f4e79"))[#align(center)[#text(fill: white, weight: "bold")[{th_nb}]]],

    {",\n\n    ".join(lignes)}
  )
]
""".strip()

    return table_typst
import pandas as pd


def generate_severity_errors_table_typst4(df_err, db_manager):
    """Génère un tableau Typst natif, compact et stylé pour les erreurs par sévérité,
    avec totaux par sévérité colorés dans un ton atténué."""

    df_err = df_err.copy()

    df_err["Severite"] = pd.to_numeric(df_err["Severite"], errors="coerce").astype("Int64")
    df_err["Nb_Erreur"] = pd.to_numeric(df_err["Nb_Erreur"], errors="coerce").astype("Int64")

    # On enlève les lignes invalides si besoin
    df_err = df_err.dropna(subset=["Severite", "Nb_Erreur", "Code_Erreur", "Description"])

    totaux_par_sev = df_err.groupby("Severite")["Nb_Erreur"].sum().to_dict()
    total_general = int(df_err["Nb_Erreur"].sum())

    # Labels traduits / échappés
    th_sev = typst_escape(db_manager.get_txt("labelsev"))
    th_code = typst_escape(db_manager.get_txt("labelctrl"))
    th_desc = typst_escape(db_manager.get_txt("labeldesc"))
    th_nb = typst_escape(db_manager.get_txt("labelnb"))
    txt_total_general = typst_escape(db_manager.get_txt("total_general"))

    def sev_color(sev_num: int) -> str:
        """Couleur forte selon la sévérité."""
        colors = {
            1: '#d32f2f',   # rouge
            2: '#f57c00',   # orange
            3: '#388e3c',   # vert
            4: '#1976d2'    # bleu
        }
        return colors.get(sev_num, '#607d8b')

    def sev_soft_color(sev_num: int) -> str:
        """Couleur atténuée pour les lignes de total par sévérité."""
        soft_colors = {
            1: '#fdecea',   # rouge très clair
            2: '#fff4e5',   # orange très clair
            3: '#edf7ed',   # vert très clair
            4: '#eaf2fb'    # bleu très clair
        }
        return soft_colors.get(sev_num, '#f3f5f7')

    def make_sev_cell(sev_num: int) -> str:
        """Cellule sévérité avec fond complètement coloré."""
        color = sev_color(sev_num)
        return (
            f'table.cell(fill: rgb("{color}"))'
            f'[#align(center)[#text(fill: white, weight: "bold")[{sev_num}]]]'
        )

    def make_text_cell(txt: str, align: str = "left", bold: bool = False) -> str:
        """Contenu de cellule texte (sans table.cell externe)."""
        txt = typst_escape(str(txt))
        if bold:
            return f'#align({align})[#text(weight: "bold")[{txt}]]'
        return f'#align({align})[{txt}]'

    def make_num_cell(value, bold: bool = False) -> str:
        """Contenu de cellule numérique aligné à droite (sans table.cell externe)."""
        if bold:
            return f'#align(right)[#text(weight: "bold")[{value}]]'
        return f'#align(right)[{value}]'

    lignes = []
    row_index = 0  # pour zebra rows

    for sev, groupe in df_err.groupby("Severite", sort=True):
        sev = int(sev)

        for _, row in groupe.iterrows():
            code = row["Code_Erreur"]
            desc = row["Description"]
            nb = int(row["Nb_Erreur"])

            # Zebra rows sur les 3 colonnes texte/nombre
            zebra_fill = 'rgb("#f7f9fb")' if row_index % 2 else 'white'

            ligne = f"""
{make_sev_cell(sev)},
table.cell(fill: {zebra_fill})[{make_text_cell(code, align="left")}],
table.cell(fill: {zebra_fill})[{make_text_cell(desc, align="left")}],
table.cell(fill: {zebra_fill})[{make_num_cell(nb)}]
""".strip()

            lignes.append(ligne)
            row_index += 1

        # Ligne total par sévérité dans un ton atténué
        total_fill = f'rgb("{sev_soft_color(sev)}")'

        lignes.append(
            f"""
table.cell(fill: {total_fill})[{make_text_cell(f"Total {sev}", align="center", bold=True)}],
table.cell(fill: {total_fill})[{make_text_cell("", bold=True)}],
table.cell(fill: {total_fill})[{make_text_cell("", bold=True)}],
table.cell(fill: {total_fill})[{make_num_cell(int(totaux_par_sev[sev]), bold=True)}]
""".strip()
        )

    # Total général (neutre, un peu plus marqué)
    lignes.append(
        f"""
table.cell(fill: rgb("#dbe5f1"))[{make_text_cell(txt_total_general, align="center", bold=True)}],
table.cell(fill: rgb("#dbe5f1"))[{make_text_cell("", bold=True)}],
table.cell(fill: rgb("#dbe5f1"))[{make_text_cell("", bold=True)}],
table.cell(fill: rgb("#dbe5f1"))[{make_num_cell(total_general, bold=True)}]
""".strip()
    )

    table_typst = f"""
#align(center)[
  #table(
    columns: (1.1fr, 2fr, 4.8fr, 1.4fr),
    inset: (x: 4pt, y: 3pt),
    column-gutter: 0pt,
    stroke: 0.6pt + rgb("#c7d0d9"),

    table.cell(fill: rgb("#1f4e79"))[#align(center)[#text(fill: white, weight: "bold")[{th_sev}]]],
    table.cell(fill: rgb("#1f4e79"))[#align(center)[#text(fill: white, weight: "bold")[{th_code}]]],
    table.cell(fill: rgb("#1f4e79"))[#align(center)[#text(fill: white, weight: "bold")[{th_desc}]]],
    table.cell(fill: rgb("#1f4e79"))[#align(center)[#text(fill: white, weight: "bold")[{th_nb}]]],

    {",\n\n    ".join(lignes)}
  )
]
""".strip()

    return table_typst


def generate_admission_table_typst(df: pd.DataFrame, db) -> str:
    """
    Génère la syntaxe Typst d'un tableau multi-entêtes d'admissions.
    Applique l'esthétique v4 et ajoute des lignes d'indicateurs de contexte à la fin.
    """
    # 1. Calculs des indicateurs globaux (Avant filtrage Top 10)
    total_global = df["occurrences"].sum() # <-- REMIS LE NOM 'total_global' ICI
    total_diags_uniques = df["code_diag"].nunique()
    
    # 2. Calculs du Top 10
    top_10_codes = (
        df.groupby("code_diag")["occurrences"]
        .sum()
        .nlargest(10)
        .index.tolist()
    )
    
    df_top10 = df[df["code_diag"].isin(top_10_codes)].copy()
    total_top10 = df_top10["occurrences"].sum()
    
    # 3. Pivot et tri des données du Top 10
    types_hospi = ['H', 'F', 'M', 'L']
    df_top10["diag_complet"] = df_top10["code_diag"] + " - " + df_top10["description"]
    
    df_pivot = df_top10.pivot(
        index="diag_complet", 
        columns="type_hospi", 
        values="occurrences"
    ).fillna(0).astype(int)
    
    # 4. Écriture du bloc de code Typst NATIF
    typst_code = []
    typst_code.append("#set text(size: 8pt)")
    typst_code.append("#v(8pt)")
    typst_code.append("#table(")
    typst_code.append("  columns: (2.5fr, " + ", ".join(["1fr, 1fr, 1fr"] * 4) + "),")
    typst_code.append("  align: (left, " + ", ".join(["right"] * 12) + "),")
    typst_code.append('  stroke: 0.3pt + rgb("#e0e0e0"),')
    
    # Gestion des arrière-plans
    typst_code.append("  fill: (x, y) => ")
    typst_code.append('    if y == 0 or y == 1 { rgb("#1a365d") }') 
    typst_code.append('    else if y == 12 { rgb("#edf2f7") }')      
    typst_code.append('    else if y >= 13 { rgb("#f8fafc") }') 
    typst_code.append('    else if calc.even(y) { rgb("#f8fafc") }') 
    typst_code.append("    else { none },")
    
    # En-tête Niveau 1 : Spanners
    typst_code.append('  table.cell(rowspan: 2, align: center + horizon, stroke: none)[#set text(fill: white); *Code & Description Diagnostic*],')
    for t in types_hospi:
        label = {"H": "Hospitalisation (H)", "F": "Ambulatoire (F)", "M": "Médecine (M)", "L": "Long Séjour (L)"}[t]
        typst_code.append(f'  table.cell(colspan: 3, align: center, stroke: none)[#set text(fill: white); *{label}*],')
        
    # En-tête Niveau 2 : Sous-colonnes
    sub_headers = []
    for _ in types_hospi:
        sub_headers.extend([
            'table.cell(stroke: none)[#set text(fill: white); *N*]', 
            'table.cell(stroke: none)[#set text(fill: white); *% Top 10*]', 
            'table.cell(stroke: none)[#set text(fill: white); *% Global*]'
        ])
    typst_code.append("  " + ", ".join(sub_headers) + ",")
    
    # Injection des lignes du Top 10 (y de 2 à 11)
    totals_occurrences = {t: 0 for t in types_hospi}
    for diag, row in df_pivot.iterrows():
        line_cells = [f"[{diag}]"]
        for t in types_hospi:
            occ = row.get(t, 0)
            totals_occurrences[t] += occ
            
            p_top10 = (occ / total_top10) * 100 if total_top10 > 0 else 0
            p_glob = (occ / total_global) * 100 if total_global > 0 else 0 # <-- PLUS D'ERREUR ICI
            
            line_cells.append(f"[{occ:,}]")
            line_cells.append(f"[{p_top10:.1f}%]")
            line_cells.append(f"[{p_glob:.1f}%]")
            
        typst_code.append("  " + ", ".join(line_cells) + ",")
        
    # 5. Ligne de Totalisation Actuelle (y = 12)
    total_line = ["[*Total (Top 10)*]"]
    for t in types_hospi:
        t_occ = totals_occurrences[t]
        t_p_top10 = (t_occ / total_top10) * 100 if total_top10 > 0 else 0
        t_p_glob = (t_occ / total_global) * 100 if total_global > 0 else 0
        
        total_line.append(f"[*{t_occ:,}*]")
        total_line.append(f"[*{t_p_top10:.1f}%*]")
        total_line.append(f"[*{t_p_glob:.1f}%*]")
    typst_code.append("  " + ", ".join(total_line) + ",")
        
    # 6. NOUVELLES LIGNES DE CONTEXTE (y = 13 et y = 14)
    lbl_total_sejours = "Nombre total de séjours (tous diagnostics confondus) :"
    typst_code.append(f'  table.cell(colspan: 12, align: right)[_ {lbl_total_sejours} _], [*{total_global:,}*],') # <-- SYNCHRONISÉ ICI AUSSI
    
    lbl_total_diags = "Nombre total de codes diagnostics (CIM-10) distincts :"
    typst_code.append(f'  table.cell(colspan: 12, align: right)[_ {lbl_total_diags} _], [*{total_diags_uniques}*]')
    
    typst_code.append(")")
    typst_code.append("#v(8pt)")
    
    return "\n".join(typst_code)

    import pandas as pd

def generate_admission_table_typst2(df: pd.DataFrame, db) -> str:
    """
    Génère la syntaxe Typst d'un tableau multi-entêtes d'admissions.
    Applique l'esthétique v4 basée sur la charte graphique page_gradient.
    """
    # 1. Calculs des indicateurs globaux (Avant filtrage Top 10)
    total_global = df["occurrences"].sum()
    total_diags_uniques = df["code_diag"].nunique()
    
    # 2. Calculs du Top 10
    top_10_codes = (
        df.groupby("code_diag")["occurrences"]
        .sum()
        .nlargest(10)
        .index.tolist()
    )
    
    df_top10 = df[df["code_diag"].isin(top_10_codes)].copy()
    total_top10 = df_top10["occurrences"].sum()
    
    # 3. Pivot et tri des données du Top 10
    types_hospi = ['H', 'F', 'M', 'L']
    df_top10["diag_complet"] = df_top10["code_diag"] + " - " + df_top10["description"]
    
    df_pivot = df_top10.pivot(
        index="diag_complet", 
        columns="type_hospi", 
        values="occurrences"
    ).fillna(0).astype(int)
    
    # 4. Écriture du bloc de code Typst NATIF
    typst_code = []
    
    # Définition locale des couleurs du dégradé pour Typst
    typst_code.append('#let brand-blue = rgb("0085e5")')
    typst_code.append('#let brand-teal = rgb("40e4ad")')
    typst_code.append('#let brand-teal-light = rgb("40e4ad").lighten(80%)')
    typst_code.append('#let bg-zebra = rgb("f8fafc")')
    
    typst_code.append("#set text(size: 8pt)")
    typst_code.append("#v(8pt)")
    typst_code.append("#table(")
    typst_code.append("  columns: (2.5fr, " + ", ".join(["1fr, 1fr, 1fr"] * 4) + "),")
    typst_code.append("  align: (left, " + ", ".join(["right"] * 12) + "),")
    typst_code.append('  stroke: 0.3pt + rgb("#e0e0e0"),')
    
    # Gestion des arrière-plans adaptée à la nouvelle charte
    typst_code.append("  fill: (x, y) => ")
    typst_code.append('    if y == 0 or y == 1 { brand-blue }')       # Bleu principal pour l'en-tête
    typst_code.append('    else if y == 12 { brand-teal-light }')    # Turquoise très clair pour le total Top 10
    typst_code.append('    else if y >= 13 { rgb("#f1f5f9") }')      # Gris neutre clair pour le contexte global
    typst_code.append('    else if calc.even(y) { bg-zebra }') 
    typst_code.append("    else { none },")
    
    # En-tête Niveau 1 : Spanners
    typst_code.append('  table.cell(rowspan: 2, align: center + horizon, stroke: none)[#set text(fill: white); *Code & Description Diagnostic*],')
    for t in types_hospi:
        label = {"H": "Hospitalisation (H)", "F": "Ambulatoire (F)", "M": "Médecine (M)", "L": "Long Séjour (L)"}[t]
        typst_code.append(f'  table.cell(colspan: 3, align: center, stroke: none)[#set text(fill: white); *{label}*],')
        
    # En-tête Niveau 2 : Sous-colonnes
    sub_headers = []
    for _ in types_hospi:
        sub_headers.extend([
            'table.cell(stroke: none)[#set text(fill: white); *N*]', 
            'table.cell(stroke: none)[#set text(fill: white); *% Top 10*]', 
            'table.cell(stroke: none)[#set text(fill: white); *% Global*]'
        ])
    typst_code.append("  " + ", ".join(sub_headers) + ",")
    
    # Injection des lignes du Top 10 (y de 2 à 11)
    totals_occurrences = {t: 0 for t in types_hospi}
    for diag, row in df_pivot.iterrows():
        line_cells = [f"[{diag}]"]
        for t in types_hospi:
            occ = row.get(t, 0)
            totals_occurrences[t] += occ
            
            p_top10 = (occ / total_top10) * 100 if total_top10 > 0 else 0
            p_glob = (occ / total_global) * 100 if total_global > 0 else 0
            
            line_cells.append(f"[{occ:,}]")
            line_cells.append(f"[{p_top10:.1f}%]")
            line_cells.append(f"[{p_glob:.1f}%]")
            
        typst_code.append("  " + ", ".join(line_cells) + ",")
        
    # 5. Ligne de Totalisation Actuelle (y = 12) - Texte en bleu pour contraster avec le fond turquoise clair
    total_line = ["[*Total (Top 10)*]"]
    for t in types_hospi:
        t_occ = totals_occurrences[t]
        t_p_top10 = (t_occ / total_top10) * 100 if total_top10 > 0 else 0
        t_p_glob = (t_occ / total_global) * 100 if total_global > 0 else 0
        
        total_line.append(f"[*{t_occ:,}*]")
        total_line.append(f"[*{t_p_top10:.1f}%*]")
        total_line.append(f"[*{t_p_glob:.1f}%*]")
    typst_code.append("  " + ", ".join(total_line) + ",")
        
    # 6. LIGNES DE CONTEXTE (y = 13 et y = 14)
    lbl_total_sejours = "Nombre total de séjours (tous diagnostics confondus) :"
    typst_code.append(f'  table.cell(colspan: 12, align: right)[_ {lbl_total_sejours} _], [*{total_global:,}*],')
    
    lbl_total_diags = "Nombre total de codes diagnostics (CIM-10) distincts :"
    typst_code.append(f'  table.cell(colspan: 12, align: right)[_ {lbl_total_diags} _], [*{total_diags_uniques}*]')
    
    typst_code.append(")")
    typst_code.append("#v(8pt)")
    
    return "\n".join(typst_code)
