#let data = json(bytes(sys.inputs.data))

#set document(title: data.name + " – Résumé", author: data.name)
#set page(paper: data.paper, margin: (x: 1.8cm, y: 1.5cm))
#set text(font: data.fonts, size: 10pt, lang: "en", hyphenate: false, ligatures: false)
#set par(justify: false, leading: 0.5em, spacing: 0.6em)
#set list(indent: 0.3em, body-indent: 0.5em, spacing: 0.4em)

#let section(title) = block(
  width: 100%,
  above: 1em,
  below: 0.55em,
  stroke: (bottom: 0.6pt),
  inset: (bottom: 2.5pt),
  text(weight: "bold", tracking: 0.05em, upper(title)),
)

#let entry(e) = {
  block(above: 0.75em, below: 0.35em, breakable: false, {
    text(size: 10.5pt, weight: "bold", e.title)
    h(1fr)
    e.dates
    if e.sub != "" {
      linebreak()
      emph(e.sub)
    }
  })
  if e.note != "" { block(above: 0.3em, below: 0.3em, strong(e.note_label + ":") + " " + e.note) }
  if e.bullets.len() > 0 { list(..e.bullets) }
}

#align(center, stack(
  spacing: 5pt,
  text(size: 22pt, weight: "bold", data.name),
  text(size: 10.5pt, data.tagline),
  text(size: 9.5pt, data.contact.join("  |  ")),
))

#for key in data.order {
  section(data.headings.at(key))
  if key == "summary" {
    data.summary
  } else if key in ("skills", "achievements") {
    for s in data.at(key) {
      block(below: 0.35em, strong(s.category + ":") + " " + s.items.join(", "))
    }
  } else if key == "certifications" {
    list(..data.certifications)
  } else {
    for e in data.at(key) { entry(e) }
  }
}
