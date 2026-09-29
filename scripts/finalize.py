"""Copy the chosen résumé version to its final file name and write report.md."""
import argparse
import json
import re
import shutil
import sys
import unicodedata
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load(path, default=None):
    """Read a UTF-8 JSON file, or return default when it doesn't exist."""
    path = Path(path)
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default


def slug(text):
    """ASCII file-name part: letters and digits joined by underscores."""
    ascii_text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[^A-Za-z0-9]+", "_", ascii_text).strip("_")


def cell(text):
    """Escape text for a Markdown table cell."""
    return str(text).replace("|", "\\|").replace("\n", " ")


def facts(ids, index):
    """Short source facts for the cited evidence IDs."""
    out = []
    for i in ids:
        ev = index.get(i)
        if ev:
            metrics = ", ".join(m["value"] for m in ev.get("metrics", []))
            out.append(ev["result"] + (f" ({metrics})" if metrics else ""))
    return "; ".join(out)


def build_report(job, n, profile, pdf_name):
    """Markdown report for the finalised version."""
    resume = load(job / f"resume.v{n}.json")
    score = load(job / f"score.v{n}.json")
    review = load(job / f"review.v{n}.json", {"issues": []})
    match = load(job / "match.json", {"gaps": []})
    analysis = load(job / "analysis.json")
    index = {ev["id"]: ev for group in ("work", "projects") for o in profile.get(group, []) for ev in o.get("evidence", [])}
    company, role = analysis["company"]["name"], analysis["job"]["title"]
    failed = [g["rule"] for g in score["gates"] if not g["ok"]]
    gaps = [f'- **{g["keyword"]}** ({g["importance"]}){": " + g["note"] if g.get("note") else ""}' for g in match["gaps"]]
    notes = [f'- {i["severity"]} ({i["lens"]}, {i["where"]}): {i["issue"]}' for i in review["issues"]]
    summary_ids = resume.get("summary_evidence_ids", [])
    lines = [
        "---",
        f"company: {json.dumps(company, ensure_ascii=False)}",
        f"role: {json.dumps(role, ensure_ascii=False)}",
        f"version: {n}",
        f'score: {score["score"]}',
        f'passed: {str(score["passed"]).lower()}',
        f"created: {date.today().isoformat()}",
        "status: ready",
        "---",
        f"# {role} at {company}",
        "",
        f"![[{pdf_name}]]",
        "",
        "## Score",
        f'**{score["score"]}/100**, target {score["target"]}, ceiling {score["ceiling"]}, '
        f'{score["pages"]} of {score["page_limit"]} page(s). Failed gates: {", ".join(failed) or "none"}.',
        "",
        "| Part | Points | Max |",
        "|---|---|---|",
        *(f'| {name} | {part["points"]} | {part["max"]} |' for name, part in score["parts"].items()),
        "",
        "## Gaps (not in your profile, so not on the résumé)",
        *(gaps or ["- None"]),
        "",
        "## Open review notes",
        *(notes or ["- None"]),
        "",
        "## Change log",
        "| Section | Change | Why |",
        "|---|---|---|",
        *(f'| {cell(c["section"])} | {cell(c["change"])} | {cell(c["why"])} |' for c in resume.get("changes", [])),
        "",
        "## Check every bullet against its evidence",
        "| Where | Résumé text | Evidence | Source facts |",
        "|---|---|---|---|",
        f'| Summary | {cell(resume["summary"])} | {", ".join(summary_ids)} | {cell(facts(summary_ids, index))} |',
    ]
    for key, name_key in (("work", "company"), ("projects", "name")):
        for item in resume.get(key, []):
            lines += [
                f'| {cell(item[name_key])} | {cell(b["text"])} | {", ".join(b["evidence_ids"])} | {cell(facts(b["evidence_ids"], index))} |'
                for b in item["bullets"]
            ]
    return "\n".join(lines) + "\n"


def main():
    """CLI: finalize.py <job_dir> <N>."""
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("job_dir")
    parser.add_argument("version", type=int)
    parser.add_argument("--profile", default=str(ROOT / "profile" / "profile.json"))
    args = parser.parse_args()

    job, n = Path(args.job_dir), args.version
    failed = [g["rule"] for g in load(job / f"score.v{n}.json")["gates"] if not g["ok"]]
    if failed:
        print(f"v{n} failed gates {failed}; not finalising.")
        return 1
    resume, analysis = load(job / f"resume.v{n}.json"), load(job / "analysis.json")
    pdf_name = "_".join(slug(s) for s in (resume["basics"]["name"], analysis["company"]["name"], analysis["job"]["title"])) + ".pdf"
    shutil.copyfile(job / f"resume.v{n}.pdf", job / pdf_name)
    (job / "report.md").write_text(build_report(job, n, load(args.profile), pdf_name), encoding="utf-8")
    print(f"Final PDF: {job / pdf_name}")
    print(f"Report: {job / 'report.md'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
