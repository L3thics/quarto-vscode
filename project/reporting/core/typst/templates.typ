#let title_block(txt) = {
  align(center)[
    == #txt
  ]
  v(10pt)
  align(center)[#line(length: 40%, stroke: 1pt + luma(180))]
  v(15pt)
}

#let section_title(txt) = {
  align(left)[
    = #txt
  ]
  v(10pt)
}

#let page_landscape() = {
  set page(width: 29.7cm, height: 21cm)
  pagebreak()
}

#let page_portrait() = {
  set page(width: 21cm, height: 29.7cm)
  pagebreak()
}

#let section_landscape(body) = {
  pagebreak()
  set page(width: 29.7cm, height: 21cm)
  body
}
