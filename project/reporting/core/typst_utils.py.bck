from turtle import color


def typst_block(content: list[str]) -> str:
    return "\n".join([
        "```{=typst}",
        *content,
        "```"
    ])
def build_section_title(titre: str, underline=False) -> str:
    content = [
        "#align(center)[",
        f"== {titre}",
        "]",
        "#v(10pt)"
    ]

    if underline:
        content.append("#align(center)[#line(length: 40%, stroke: 1pt + luma(180))]")

    content.append("#v(15pt)")

    return typst_block(content)


def build_txt_block(
    txt: str,
    size: str = "10pt",
    font: str = "Arial",
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
    font: str = "Arial"
) -> str:

    return typst_block([
        f"#set text(size: {font_size})",
        f"#set text(font: \"{font}\")",
        f"#align({align})[",
        table_md,
        "]"
    ])

# def build_table_block(
#     table_md: str,
#     align: str = "center",
#     font_size: str = "10pt"
# ) -> str:

#     return typst_block([
#         f"#set text(size: {font_size})",
#         f"#align({align})[",
#         "#box(width: 100%)[",
#         table_md,
#         "]",
#         "]"
#     ])

