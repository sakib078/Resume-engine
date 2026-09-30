"""Render a tailored résumé JSON to PDF with the Typst template."""
import argparse
import json
import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "templates" / "harvard.typ"
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
HEADINGS = {
    "summary": "Summary",
    "experience": "Experience",
    "projects": "Projects",
    "education": "Education",
    "skills": "Skills",
    "certifications": "Certifications",
    "achievements": "Achievements",
}


def load_config():
    """Read config.toml."""
    return tomllib.loads((ROOT / "config.toml").read_text(encoding="utf-8"))


def fmt_month(value):
    """'2023-04' -> 'Apr 2023'; 'present' -> 'Present'."""
    if not value:
        return ""
    if value == "present":
        return "Present"
    year, month = value.split("-")[:2]
    return f"{MONTHS[int(month) - 1]} {year}"


def date_range(start, end):
    """'Mon YYYY – Mon YYYY', or a single date when only one is known."""
    if start and end:
        return f"{fmt_month(start)} – {fmt_month(end)}"
    return fmt_month(start or end)


def join(*parts, sep=" | "):
    """Join the non-empty parts."""
    return sep.join(p for p in parts if p)


def short_url(url):
    """Display form of a URL: no scheme, no 'www.', no trailing slash."""
    return re.sub(r"^(https?://)?(www\.)?", "", url or "").rstrip("/")


def full_url(url):
    """Link target for a URL that may lack a scheme."""
    return url if re.match(r"^[a-z]+:", url) else "https://" + url


def contact(resume):
    """Header items in display order: location, phone, email, then links."""
    basics = resume["basics"]
    items = [{"text": basics[k], "url": ""} for k in ("location", "phone") if basics.get(k)]
    if basics.get("email"):
        items.append({"text": basics["email"], "url": "mailto:" + basics["email"]})
    urls = [basics[k] for k in ("website", "github", "linkedin") if basics.get(k)]
    urls += [link["url"] for link in resume.get("links", [])]
    return items + [{"text": short_url(u), "url": full_url(u)} for u in urls]


def section_order(resume):
    """Keys of the non-empty sections, in render order."""
    filled = {
        "summary": resume.get("summary"),
        "skills": resume.get("skills"),
        "experience": resume.get("work"),
        "projects": resume.get("projects"),
        "education": resume.get("education"),
        "certifications": resume.get("certificates"),
        "achievements": resume.get("achievements"),
    }
    order = list(HEADINGS)
    if resume.get("education_first"):
        order.remove("education")
        order.insert(order.index("experience"), "education")
    return [key for key in order if filled[key]]


def entry(title, dates, left, right, bullets, note=""):
    """Two-row heading (title and dates; place and location), an optional note and bullet texts."""
    return {"title": title, "dates": dates, "left": left, "right": right, "note": note, "bullets": [b["text"] for b in bullets]}


def display_data(resume, config):
    """Display-ready dictionary read by templates/harvard.typ."""
    return {
        "paper": config["render"]["paper"],
        "fonts": config["render"]["fonts"],
        "name": resume["basics"]["name"],
        "tagline": resume.get("tagline", ""),
        "contact": contact(resume),
        "headings": HEADINGS,
        "order": section_order(resume),
        "summary": resume.get("summary", ""),
        "skills": resume.get("skills", []),
        "experience": [
            entry(w["title"], date_range(w.get("start"), w.get("end")), w["company"], w.get("location", ""), w["bullets"])
            for w in resume.get("work", [])
        ],
        "projects": [
            {
                "name": p["name"],
                "url": full_url(p["link"]) if p.get("link") else "",
                "tech": ", ".join(p.get("tech_stack", [])),
                "bullets": [b["text"] for b in p["bullets"]],
            }
            for p in resume.get("projects", [])
        ],
        "education": [
            entry(
                join(join(e["degree"], e.get("field"), sep=" in "), e.get("grade"), sep=", "),
                date_range(e.get("start"), e.get("end")),
                e["institution"],
                e.get("location", ""),
                [],
                "Relevant Coursework: " + ", ".join(e["coursework"]) if e.get("coursework") else "",
            )
            for e in resume.get("education", [])
        ],
        "certifications": [
            join(c["name"], join(c.get("issuer"), fmt_month(c.get("date")), sep=", "), sep=" — ")
            for c in resume.get("certificates", [])
        ],
        "achievements": resume.get("achievements", []),
    }


def render(resume_path, out_path, config=None):
    """Compile one résumé JSON to PDF."""
    import typst

    data = display_data(json.loads(Path(resume_path).read_text(encoding="utf-8")), config or load_config())
    typst.compile(str(TEMPLATE), output=str(out_path), sys_inputs={"data": json.dumps(data, ensure_ascii=False)})


def main():
    """CLI: render.py <resume.json> <out.pdf>."""
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("resume")
    parser.add_argument("out")
    args = parser.parse_args()
    render(args.resume, args.out)
    print(f"Rendered {args.out}")


if __name__ == "__main__":
    main()
