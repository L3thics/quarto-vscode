function Meta(meta)
  -- 1. Récupère le paramètre 'lang' (ex: envoyé par -P lang=fr)
  local lang = "bi"
  if meta.params and meta.params.lang then
    lang = pandoc.utils.stringify(meta.params.lang)
  end

  -- 2. Modifie dynamiquement le nom du fichier de sortie attendu par Quarto
  meta["output-file"] = "rapport_SH_Z_3_1_" .. lang .. ".pdf"
  
  return meta
end
