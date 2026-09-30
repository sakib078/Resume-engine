#let data = json(bytes(sys.inputs.data))
#let small = 10pt

#set document(title: data.name + " – Résumé", author: data.name)
#set page(paper: data.paper, margin: (x: 0.45in, y: 0.4in))
#set text(font: data.fonts, size: 11pt, lang: "en", hyphenate: false, ligatures: false)
#set par(justify: false, leading: 0.45em, spacing: 0.45em)
#set list(indent: 0.3in, body-indent: 0.45em, spacing: 0.4em, marker: text(size: 0.75em, sym.bullet))

#let section(title) = block(
  width: 100%,
  above: 0.85em,
  below: 0.45em,
  stroke: (bottom: 0.5pt),
  inset: (bottom: 2pt),
  text(size: 12pt, smallcaps(title)),
)

#let indented(body) = block(width: 100%, inset: (left: 0.15in, right: 0.08in), body)

#let entry(e) = {
  block(above: 0.6em, below: 0.35em, breakable: false, width: 100%, inset: (left: 0.15in, right: 0.08in), {
    strong(e.title)
    h(1fr)
    e.dates
    if e.left != "" or e.right != "" {
      linebreak()
      text(size: small, emph(e.left))
      h(1fr)
      text(size: small, emph(e.right))
    }
  })
  if e.note != "" { indented(text(size: small, e.note)) }
  if e.bullets.len() > 0 {
    set text(size: small)
    list(..e.bullets)
  }
}

#let project(p) = {
  block(above: 0.6em, below: 0.35em, breakable: false, width: 100%, inset: (left: 0.15in, right: 0.08in), text(size: small, {
    if p.url != "" { link(p.url, strong(p.name)) } else { strong(p.name) }
    if p.tech != "" { " | "; emph(p.tech) }
  }))
  if p.bullets.len() > 0 {
    set text(size: small)
    list(..p.bullets)
  }
}

#align(center, stack(
  spacing: 5pt,
  text(size: 24pt, weight: "bold", smallcaps(data.name)),
  text(style: "italic", data.tagline),
  text(size: small, data.contact.map(c => if c.url != "" { underline(link(c.url, c.text)) } else { c.text }).join("  |  ")),
))

#for key in data.order {
  section(data.headings.at(key))
  if key == "summary" {
    indented(text(size: small, data.summary))
  } else if key in ("skills", "achievements") {
    indented(text(size: small, {
      set par(hanging-indent: 0.15in)
      for s in data.at(key) {
        block(below: 0.3em, strong(s.category) + ": " + s.items.join(", "))
      }
    }))
  } else if key == "certifications" {
    set text(size: small)
    list(..data.certifications)
  } else if key == "projects" {
    for p in data.projects { project(p) }
  } else {
    for e in data.at(key) { entry(e) }
  }
}
