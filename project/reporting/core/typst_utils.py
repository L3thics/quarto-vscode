from turtle import color


def typst_block(content: list[str]) -> str:
    return "\n".join([
        "```{=typst}",
        *content,
        "```"
    ])

def build_section_title(titre: str, underline=False) -> str:
    # Pour changer le style visuel de TOUS les titres de niveau 2 (==) sans casser les signets PDF
    content = [
        "#show heading.where(level: 2): it => [",
        "  #set align(center)",
        "  #set text(weight: \"bold\")",
        "  #it.body",
        "]",
        f"== {titre}",  # Ce titre crée automatiquement le signet cliquable à gauche
        "#v(10pt)"
    ]

    if underline:
        content.append("#align(center)[#line(length: 40%, stroke: 1pt + luma(180))]")

    content.append("#v(15pt)")

    return typst_block(content)


def build_txt_block(
    txt: str,
    size: str = "8pt",
    font: str = "Open Sans",
    bold: bool = False,
    color: str = "black"
) -> str:

    content = [
        f"#set text(size: {size})",
        f"#set text(font: \"{font}\")"
    ]

    if bold:
        content.append("#set text(weight: \"bold\")")
    if color:
        content.append(f"#set text(fill: {color})")
    content += [
        "#align(left)[",
        txt.replace("\n", " #linebreak() "),
        "]"
    ]

    return typst_block(content)

def build_table_block(
    table_md: str,
    align: str = "center",
    font_size: str = "10pt",
    font: str = "Open Sans"
) -> str:

    return typst_block([
        f"#set text(size: {font_size})",
        f"#set text(font: \"{font}\")",
        f"#align({align})[",
        table_md,
        "]"
    ])
