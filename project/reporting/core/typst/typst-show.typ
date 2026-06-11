#show: doc => {
  let vars = json("core/typst/vars.json")
  let banner-path = vars.at("banner-path", default: "")
  
  set page(
    paper: "a4",
    // Toutes les pages partagent désormais la même marge propre de 2.5cm
    margin: (x: 2.5cm, top: 2.5cm, bottom: 2.5cm),
    
    // Le footer est configuré globalement
    footer: context [
      #set text(8pt, fill: luma(120))
      #line(length: 100%, stroke: 0.5pt + luma(150))
      #grid(
        columns: (1fr, 1fr),
        align(left)[#vars.at("footer-left", default: "")],
        align(right)[Page #counter(page).display() / #counter(page).final().at(0)]
      )
    ]
  )
  
  // Si une bannière est définie, on l'affiche TOUT EN HAUT du flux du document
  if banner-path != "" {
    // block permet d'isoler l'image pour qu'aucun élément ou texte ne vienne dessus
    block(width: 100%, inset: (bottom: 0cm))[
      #align(left, image(banner-path, width: 60%))
    ]
  }
  
  doc
}
