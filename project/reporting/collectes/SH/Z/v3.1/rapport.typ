// Some definitions presupposed by pandoc's typst output.
#let blockquote(body) = [
  #set text( size: 0.92em )
  #block(inset: (left: 1.5em, top: 0.2em, bottom: 0.2em))[#body]
]

#let horizontalrule = [
  #line(start: (25%,0%), end: (75%,0%))
]

#let endnote(num, contents) = [
  #stack(dir: ltr, spacing: 3pt, super[#num], contents)
]

#show terms: it => {
  it.children
    .map(child => [
      #strong[#child.term]
      #block(inset: (left: 1.5em, top: -0.4em))[#child.description]
      ])
    .join()
}

// Some quarto-specific definitions.

#show raw.where(block: true): set block(
    fill: luma(230),
    width: 100%,
    inset: 8pt,
    radius: 2pt
  )

#let block_with_new_content(old_block, new_content) = {
  let d = (:)
  let fields = old_block.fields()
  fields.remove("body")
  if fields.at("below", default: none) != none {
    // TODO: this is a hack because below is a "synthesized element"
    // according to the experts in the typst discord...
    fields.below = fields.below.amount
  }
  return block.with(..fields)(new_content)
}

#let empty(v) = {
  if type(v) == "string" {
    // two dollar signs here because we're technically inside
    // a Pandoc template :grimace:
    v.matches(regex("^\\s*$")).at(0, default: none) != none
  } else if type(v) == "content" {
    if v.at("text", default: none) != none {
      return empty(v.text)
    }
    for child in v.at("children", default: ()) {
      if not empty(child) {
        return false
      }
    }
    return true
  }

}

// Subfloats
// This is a technique that we adapted from https://github.com/tingerrr/subpar/
#let quartosubfloatcounter = counter("quartosubfloatcounter")

#let quarto_super(
  kind: str,
  caption: none,
  label: none,
  supplement: str,
  position: none,
  subrefnumbering: "1a",
  subcapnumbering: "(a)",
  body,
) = {
  context {
    let figcounter = counter(figure.where(kind: kind))
    let n-super = figcounter.get().first() + 1
    set figure.caption(position: position)
    [#figure(
      kind: kind,
      supplement: supplement,
      caption: caption,
      {
        show figure.where(kind: kind): set figure(numbering: _ => numbering(subrefnumbering, n-super, quartosubfloatcounter.get().first() + 1))
        show figure.where(kind: kind): set figure.caption(position: position)

        show figure: it => {
          let num = numbering(subcapnumbering, n-super, quartosubfloatcounter.get().first() + 1)
          show figure.caption: it => {
            num.slice(2) // I don't understand why the numbering contains output that it really shouldn't, but this fixes it shrug?
            [ ]
            it.body
          }

          quartosubfloatcounter.step()
          it
          counter(figure.where(kind: it.kind)).update(n => n - 1)
        }

        quartosubfloatcounter.update(0)
        body
      }
    )#label]
  }
}

// callout rendering
// this is a figure show rule because callouts are crossreferenceable
#show figure: it => {
  if type(it.kind) != "string" {
    return it
  }
  let kind_match = it.kind.matches(regex("^quarto-callout-(.*)")).at(0, default: none)
  if kind_match == none {
    return it
  }
  let kind = kind_match.captures.at(0, default: "other")
  kind = upper(kind.first()) + kind.slice(1)
  // now we pull apart the callout and reassemble it with the crossref name and counter

  // when we cleanup pandoc's emitted code to avoid spaces this will have to change
  let old_callout = it.body.children.at(1).body.children.at(1)
  let old_title_block = old_callout.body.children.at(0)
  let old_title = old_title_block.body.body.children.at(2)

  // TODO use custom separator if available
  let new_title = if empty(old_title) {
    [#kind #it.counter.display()]
  } else {
    [#kind #it.counter.display(): #old_title]
  }

  let new_title_block = block_with_new_content(
    old_title_block, 
    block_with_new_content(
      old_title_block.body, 
      old_title_block.body.body.children.at(0) +
      old_title_block.body.body.children.at(1) +
      new_title))

  block_with_new_content(old_callout,
    block(below: 0pt, new_title_block) +
    old_callout.body.children.at(1))
}

// 2023-10-09: #fa-icon("fa-info") is not working, so we'll eval "#fa-info()" instead
#let callout(body: [], title: "Callout", background_color: rgb("#dddddd"), icon: none, icon_color: black) = {
  block(
    breakable: false, 
    fill: background_color, 
    stroke: (paint: icon_color, thickness: 0.5pt, cap: "round"), 
    width: 100%, 
    radius: 2pt,
    block(
      inset: 1pt,
      width: 100%, 
      below: 0pt, 
      block(
        fill: background_color, 
        width: 100%, 
        inset: 8pt)[#text(icon_color, weight: 900)[#icon] #title]) +
      if(body != []){
        block(
          inset: 1pt, 
          width: 100%, 
          block(fill: white, width: 100%, inset: 8pt, body))
      }
    )
}



#let article(
  title: none,
  subtitle: none,
  authors: none,
  date: none,
  abstract: none,
  abstract-title: none,
  cols: 1,
  margin: (x: 1.25in, y: 1.25in),
  paper: "us-letter",
  lang: "en",
  region: "US",
  font: "linux libertine",
  fontsize: 11pt,
  title-size: 1.5em,
  subtitle-size: 1.25em,
  heading-family: "linux libertine",
  heading-weight: "bold",
  heading-style: "normal",
  heading-color: black,
  heading-line-height: 0.65em,
  sectionnumbering: none,
  toc: false,
  toc_title: none,
  toc_depth: none,
  toc_indent: 1.5em,
  doc,
) = {
  set page(
    paper: paper,
    margin: margin,
    numbering: "1",
  )
  set par(justify: true)
  set text(lang: lang,
           region: region,
           font: font,
           size: fontsize)
  set heading(numbering: sectionnumbering)
  if title != none {
    align(center)[#block(inset: 2em)[
      #set par(leading: heading-line-height)
      #if (heading-family != none or heading-weight != "bold" or heading-style != "normal"
           or heading-color != black or heading-decoration == "underline"
           or heading-background-color != none) {
        set text(font: heading-family, weight: heading-weight, style: heading-style, fill: heading-color)
        text(size: title-size)[#title]
        if subtitle != none {
          parbreak()
          text(size: subtitle-size)[#subtitle]
        }
      } else {
        text(weight: "bold", size: title-size)[#title]
        if subtitle != none {
          parbreak()
          text(weight: "bold", size: subtitle-size)[#subtitle]
        }
      }
    ]]
  }

  if authors != none {
    let count = authors.len()
    let ncols = calc.min(count, 3)
    grid(
      columns: (1fr,) * ncols,
      row-gutter: 1.5em,
      ..authors.map(author =>
          align(center)[
            #author.name \
            #author.affiliation \
            #author.email
          ]
      )
    )
  }

  if date != none {
    align(center)[#block(inset: 1em)[
      #date
    ]]
  }

  if abstract != none {
    block(inset: 2em)[
    #text(weight: "semibold")[#abstract-title] #h(1em) #abstract
    ]
  }

  if toc {
    let title = if toc_title == none {
      auto
    } else {
      toc_title
    }
    block(above: 0em, below: 2em)[
    #outline(
      title: toc_title,
      depth: toc_depth,
      indent: toc_indent
    );
    ]
  }

  if cols == 1 {
    doc
  } else {
    columns(cols, doc)
  }
}

#set table(
  inset: 6pt,
  stroke: none
)
#import "../../../../core/typst/templates.typ": *
#set page(
  footer: context [
    #set text(8pt, fill: luma(120))
    #line(length: 100%, stroke: 0.5pt + luma(150))
    #grid(
      columns: (1fr, 1fr),
      align(left)[Confidential / Vertrouwelijk],
      align(right)[Page #counter(page).display() / #counter(page).final().at(0)]
    )
  ]
)
#set table(stroke: 0.5pt + rgb("#bdc3c7"))

#show: doc => article(
  margin: (x: 2.5cm,y: 2.5cm,),
  paper: "a4",
  toc_title: [Table of contents],
  toc_depth: 3,
  cols: 1,
  doc,
)

/*
#pagebreak()

#set page(
  width: 29.7cm,
  height: 21cm
)*/
#block[
#block[
```
LABELS PATH = /workspaces/quarto-vscode/project/reporting/data/labels.csv
```

]
] <init-modules>
#align(left)[
#box(image("SPF_BI-LANGUE.jpg", width: 50%))
]
#align(center)[
  == [Z]
]
#v(10pt)
#align(center)[#line(length: 40%, stroke: 1pt + luma(180))]
#v(15pt)
#align(center)[
#align(center)[
  #table(
    columns: (2fr, 2fr),
    column-gutter: 5pt,
    stroke: white,
    inset: (x: 4pt, y: 2pt),
    [#align(right)[[HosName]]] , [#align(left)[CHR Namur]] , [#align(right)[[year]]] , [#align(left)[2026]] , [#align(right)[[periode]]] , [#align(left)[Semestre 1]]
  )
]
]
#align(center)[
  == [ReportTitle]
]
#v(15pt)
#[
#set text(font: ("-apple-system", "BlinkMacSystemFont", "Segoe UI", "Roboto", "Oxygen", "Ubuntu", "Cantarell", "Helvetica Neue", "Fira Sans", "Droid Sans", "Arial", "sans-serif") , size: 12pt); #table(
  columns: 4,
  align: (left,left,left,right,),
  table.header(table.cell(align: bottom + left, fill: rgb("#ffffff"))[#set text(size: 1.0em , fill: rgb("#333333")); \[labelsev\]], table.cell(align: bottom + left, fill: rgb("#ffffff"))[#set text(size: 1.0em , fill: rgb("#333333")); \[labelctrl\]], table.cell(align: bottom + left, fill: rgb("#ffffff"))[#set text(size: 1.0em , fill: rgb("#333333")); \[labeldesc\]], table.cell(align: bottom + right, fill: rgb("#ffffff"))[#set text(size: 1.0em , fill: rgb("#333333")); \[labelnb\]],),
  table.hline(),
  table.cell(align: horizon + left, fill: rgb("#e74c3c"), stroke: (top: (paint: rgb("#d3d3d3"), thickness: 0.75pt)))[#set text(fill: white); 1], table.cell(align: horizon + left, stroke: (top: (paint: rgb("#d3d3d3"), thickness: 0.75pt)))[ERR-101], table.cell(align: horizon + left, stroke: (top: (paint: rgb("#d3d3d3"), thickness: 0.75pt)))[Panne serveur], table.cell(align: horizon + right, stroke: (top: (paint: rgb("#d3d3d3"), thickness: 0.75pt)))[5],
  table.cell(align: horizon + left, fill: rgb("#e74c3c"), stroke: (top: (paint: rgb("#d3d3d3"), thickness: 0.75pt)))[#set text(fill: white); 1], table.cell(align: horizon + left, stroke: (top: (paint: rgb("#d3d3d3"), thickness: 0.75pt)))[ERR-102], table.cell(align: horizon + left, stroke: (top: (paint: rgb("#d3d3d3"), thickness: 0.75pt)))[Crash DB], table.cell(align: horizon + right, stroke: (top: (paint: rgb("#d3d3d3"), thickness: 0.75pt)))[2],
  table.cell(align: horizon + left, fill: rgb("#f4f6f7"), stroke: (top: (paint: rgb("#d3d3d3"), thickness: 0.75pt)))[Total 1], table.cell(align: horizon + left, fill: rgb("#f4f6f7"), stroke: (top: (paint: rgb("#d3d3d3"), thickness: 0.75pt)))[], table.cell(align: horizon + left, fill: rgb("#f4f6f7"), stroke: (top: (paint: rgb("#d3d3d3"), thickness: 0.75pt)))[], table.cell(align: horizon + right, fill: rgb("#f4f6f7"), stroke: (top: (paint: rgb("#d3d3d3"), thickness: 0.75pt)))[7],
  table.cell(align: horizon + left, fill: rgb("#e67e22"), stroke: (top: (paint: rgb("#d3d3d3"), thickness: 0.75pt)))[#set text(fill: white); 2], table.cell(align: horizon + left, stroke: (top: (paint: rgb("#d3d3d3"), thickness: 0.75pt)))[ERR-201], table.cell(align: horizon + left, stroke: (top: (paint: rgb("#d3d3d3"), thickness: 0.75pt)))[Timeout API], table.cell(align: horizon + right, stroke: (top: (paint: rgb("#d3d3d3"), thickness: 0.75pt)))[12],
  table.cell(align: horizon + left, fill: rgb("#e67e22"), stroke: (top: (paint: rgb("#d3d3d3"), thickness: 0.75pt)))[#set text(fill: white); 2], table.cell(align: horizon + left, stroke: (top: (paint: rgb("#d3d3d3"), thickness: 0.75pt)))[ERR-202], table.cell(align: horizon + left, stroke: (top: (paint: rgb("#d3d3d3"), thickness: 0.75pt)))[Disque 80%], table.cell(align: horizon + right, stroke: (top: (paint: rgb("#d3d3d3"), thickness: 0.75pt)))[4],
  table.cell(align: horizon + left, fill: rgb("#f4f6f7"), stroke: (top: (paint: rgb("#d3d3d3"), thickness: 0.75pt)))[Total 2], table.cell(align: horizon + left, fill: rgb("#f4f6f7"), stroke: (top: (paint: rgb("#d3d3d3"), thickness: 0.75pt)))[], table.cell(align: horizon + left, fill: rgb("#f4f6f7"), stroke: (top: (paint: rgb("#d3d3d3"), thickness: 0.75pt)))[], table.cell(align: horizon + right, fill: rgb("#f4f6f7"), stroke: (top: (paint: rgb("#d3d3d3"), thickness: 0.75pt)))[16],
  table.cell(align: horizon + left, fill: rgb("#2ecc71"), stroke: (top: (paint: rgb("#d3d3d3"), thickness: 0.75pt)))[#set text(fill: white); 3], table.cell(align: horizon + left, stroke: (top: (paint: rgb("#d3d3d3"), thickness: 0.75pt)))[ERR-301], table.cell(align: horizon + left, stroke: (top: (paint: rgb("#d3d3d3"), thickness: 0.75pt)))[Session exp.], table.cell(align: horizon + right, stroke: (top: (paint: rgb("#d3d3d3"), thickness: 0.75pt)))[45],
  table.cell(align: horizon + left, fill: rgb("#2ecc71"), stroke: (top: (paint: rgb("#d3d3d3"), thickness: 0.75pt)))[#set text(fill: white); 3], table.cell(align: horizon + left, stroke: (top: (paint: rgb("#d3d3d3"), thickness: 0.75pt)))[ERR-302], table.cell(align: horizon + left, stroke: (top: (paint: rgb("#d3d3d3"), thickness: 0.75pt)))[Lenteur], table.cell(align: horizon + right, stroke: (top: (paint: rgb("#d3d3d3"), thickness: 0.75pt)))[8],
  table.cell(align: horizon + left, fill: rgb("#f4f6f7"), stroke: (top: (paint: rgb("#d3d3d3"), thickness: 0.75pt)))[Total 3], table.cell(align: horizon + left, fill: rgb("#f4f6f7"), stroke: (top: (paint: rgb("#d3d3d3"), thickness: 0.75pt)))[], table.cell(align: horizon + left, fill: rgb("#f4f6f7"), stroke: (top: (paint: rgb("#d3d3d3"), thickness: 0.75pt)))[], table.cell(align: horizon + right, fill: rgb("#f4f6f7"), stroke: (top: (paint: rgb("#d3d3d3"), thickness: 0.75pt)))[53],
  table.cell(align: horizon + left, fill: rgb("#eaeded"), stroke: (top: (paint: rgb("#d3d3d3"), thickness: 0.75pt)))[\[total\_general\]], table.cell(align: horizon + left, fill: rgb("#eaeded"), stroke: (top: (paint: rgb("#d3d3d3"), thickness: 0.75pt)))[], table.cell(align: horizon + left, fill: rgb("#eaeded"), stroke: (top: (paint: rgb("#d3d3d3"), thickness: 0.75pt)))[], table.cell(align: horizon + right, fill: rgb("#eaeded"), stroke: (top: (paint: rgb("#d3d3d3"), thickness: 0.75pt)))[76],
)
]
#v(25pt)
#par(justify: true)[

[sev11]
[sev12]

[sev21]
[sev22]

[sev31]
[sev32]
[sev41]
[sev42]

]
#pagebreak()
#align(center)[
  == [ReportTitle]
]
#v(15pt)
#block[

#align(center)[
  #table(
    columns: (1.2fr, 2fr, 4fr, 1.5fr),
    column-gutter: 0pt,
    inset: (x: 6pt, y: 4pt),
    stroke: 0.5pt + rgb("#bdc3c7"),

    [#text(weight: "bold")[[labelsev]]],
    [#text(weight: "bold")[[labelctrl]]],
    [#text(weight: "bold")[[labeldesc]]],
    [#align(right)[#text(weight: "bold")[[labelnb ]]]],

    [#rect(fill: rgb("#e74c3c"), inset: 4pt)[#text(fill: white, weight: "bold")[1]]],
[#align(left)[ERR-101]],
[#align(left)[Panne serveur]],
[#align(right)[5]],

    [#rect(fill: rgb("#e74c3c"), inset: 4pt)[#text(fill: white, weight: "bold")[1]]],
[#align(left)[ERR-102]],
[#align(left)[Crash DB]],
[#align(right)[2]],

    [#text(weight: "bold")[Total 1]],
[#text(weight: "bold")[]],
[#text(weight: "bold")[]],
[#align(right)[#text(weight: "bold")[7]]],

    [#rect(fill: rgb("#e67e22"), inset: 4pt)[#text(fill: white, weight: "bold")[2]]],
[#align(left)[ERR-201]],
[#align(left)[Timeout API]],
[#align(right)[12]],

    [#rect(fill: rgb("#e67e22"), inset: 4pt)[#text(fill: white, weight: "bold")[2]]],
[#align(left)[ERR-202]],
[#align(left)[Disque 80%]],
[#align(right)[4]],

    [#text(weight: "bold")[Total 2]],
[#text(weight: "bold")[]],
[#text(weight: "bold")[]],
[#align(right)[#text(weight: "bold")[16]]],

    [#rect(fill: rgb("#2ecc71"), inset: 4pt)[#text(fill: white, weight: "bold")[3]]],
[#align(left)[ERR-301]],
[#align(left)[Session exp.]],
[#align(right)[45]],

    [#rect(fill: rgb("#2ecc71"), inset: 4pt)[#text(fill: white, weight: "bold")[3]]],
[#align(left)[ERR-302]],
[#align(left)[Lenteur]],
[#align(right)[8]],

    [#text(weight: "bold")[Total 3]],
[#text(weight: "bold")[]],
[#text(weight: "bold")[]],
[#align(right)[#text(weight: "bold")[53]]],

    [#text(weight: "bold")[Total général]],
[#text(weight: "bold")[]],
[#text(weight: "bold")[]],
[#align(right)[#text(weight: "bold")[76]]]
  )
]
] <tableau-erreurs2>
#v(25pt)
#par(justify: true)[

[sev11]
[sev12]

[sev21]
[sev22]

[sev31]
[sev32]
[sev41]
[sev42]

]
#page_landscape()


#title_block("TEST_SECTION 0")
#title_block("[ReportTitle]")
#section_landscape([#title_block("[ReportTitle]")])
#align(center)[
#align(center)[
  #table(
    columns: (2fr, 2fr),
    column-gutter: 5pt,
    stroke: white,
    inset: (x: 4pt, y: 2pt),
    [#align(right)[[HosName]]] , [#align(left)[CHR Namur]] , [#align(right)[[year]]] , [#align(left)[2026]] , [#align(right)[[periode]]] , [#align(left)[Semestre 1]]
  )
]
]




