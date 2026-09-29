"""Render a tailored résumé JSON to PDF with the Harvard Typst template."""
import argparse
import json
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "templates" / "harvard.typ"
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
HEADINGS = {
    "summary": "Summary",
    "skills": "Skills",
    "experience": "Experience",
    "projects": "Projects",
    "education": "Education",
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


def entry(title, dates, sub, bullets, note_label="", note=""):
    """One heading line, an optional labelled note and bullet texts, as the template expects."""
    return {"title": title, "dates": dates, "sub": sub, "note_label": note_label, "note": note, "bullets": [b["text"] for b in bullets]}


def display_data(resume, config):
    """Display-ready dictionary read by templates/harvard.typ."""
    basics = resume["basics"]
    return {
        "paper": config["render"]["paper"],
        "fonts": config["render"]["fonts"],
        "name": basics["name"],
        "tagline": resume.get("tagline", ""),
        "contact": [basics[k] for k in ("email", "phone", "location", "linkedin", "website", "github") if basics.get(k)]
        + [link["url"] for link in resume.get("links", [])],
        "headings": HEADINGS,
        "order": section_order(resume),
        "summary": resume.get("summary", ""),
        "skills": resume.get("skills", []),
        "experience": [
            entry(w["title"], date_range(w.get("start"), w.get("end")), join(w["company"], w.get("location")), w["bullets"])
            for w in resume.get("work", [])
        ],
        "projects": [
            entry(p["name"], date_range(p.get("start"), p.get("end")), p.get("link", ""), p["bullets"])
            for p in resume.get("projects", [])
        ],
        "education": [
            entry(
                join(join(e["degree"], e.get("field"), sep=" in "), e.get("grade"), sep=", "),
                fmt_month(e.get("end")),
                join(e["institution"], e.get("location"), sep=", "),
                [],
                "Relevant coursework" if e.get("coursework") else "",
                ", ".join(e.get("coursework", [])),
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
