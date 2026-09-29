"""Deterministic ATS scorer: hard gates, a 0-100 score, fixes and the reachable ceiling for one job."""
import argparse
import json
import re
import sys
import unicodedata
from collections import Counter
from datetime import date
from pathlib import Path

from render import HEADINGS, display_data, load_config, section_order

ROOT = Path(__file__).resolve().parent.parent
NUMBER = re.compile(r"(?<![A-Za-z0-9-])\d+(?:[.,]\d+)*")
YEARS = re.compile(r"(\d+)\+?\s*years?", re.I)
PLACEHOLDER = re.compile(r"\[[^\]]*\]|\bX+%|\bTBD\b|\?\?")
PRONOUN = re.compile(r"\bI\b|\b[Mm](?:e|y|ine|yself)\b")
LIGATURE = re.compile("[ﬀ-ﬆ-]")
QUANT_WORDS = re.compile(r"\b(?:doubled|tripled|quadrupled|halved)\b", re.I)
TITLE_NOISE = {
    "senior", "sr", "junior", "jr", "lead", "principal", "staff", "head", "chief", "graduate",
    "intern", "associate", "entry", "level", "mid", "i", "ii", "iii", "iv", "of", "and", "the",
}
TRANSLATE = str.maketrans({
    "‘": "'", "’": "'", "“": '"', "”": '"',
    "–": "-", "—": "-", "−": "-", "•": " ", " ": " ",
})


def clean(text):
    """NFKC-normalise and unify quotes, dashes and bullet glyphs."""
    return unicodedata.normalize("NFKC", text or "").translate(TRANSLATE)


def squash(text):
    """Cleaned, lowercased text with all whitespace removed."""
    return re.sub(r"\s+", "", clean(text).lower())


def load_json(path):
    """Read a UTF-8 JSON file."""
    return json.loads(Path(path).read_text(encoding="utf-8"))


def load_lines(path):
    """Read a word list, skipping blanks and # comments."""
    lines = (line.strip() for line in Path(path).read_text(encoding="utf-8").splitlines())
    return [line for line in lines if line and not line.startswith("#")]


def load_rules():
    """Lexicon groups, action verbs and banned phrases."""
    lexicon = load_json(ROOT / "rules" / "lexicon.json")
    return {
        "groups": [[name, *aliases] for category in lexicon.values() for name, aliases in category.items()],
        "verbs": {v.lower() for v in load_lines(ROOT / "rules" / "action-verbs.txt")},
        "banned": [p.lower() for p in load_lines(ROOT / "rules" / "banned-phrases.txt")],
    }


def variants(term, aliases, groups):
    """A keyword's spellings: its own aliases plus any lexicon group it belongs to."""
    names = {term, *aliases}
    lowered = {n.lower() for n in names}
    for group in groups:
        if lowered & {g.lower() for g in group}:
            names.update(group)
    return names


def keyword_regex(names):
    """One regex for all spellings; spellings of two characters or fewer are case-sensitive."""
    parts = []
    for name in sorted({n.strip() for n in names if n.strip()}, key=len, reverse=True):
        if len(name) <= 2:
            parts.append(rf"(?<![A-Za-z0-9]){re.escape(name)}(?![A-Za-z0-9&'])")
        else:
            body = r"[\s-]+".join(re.escape(word) for word in name.split())
            parts.append(rf"(?i:(?<![A-Za-z0-9]){body}(?:e?s)?(?![A-Za-z0-9]))")
    return re.compile("|".join(parts))


def evidence_index(profile):
    """Map evidence ID to (owner ID, evidence) across roles and projects."""
    return {
        ev["id"]: (owner["id"], ev)
        for group in ("work", "projects")
        for owner in profile.get(group, [])
        for ev in owner.get("evidence", [])
    }


def evidence_text(ev):
    """Every text field of one evidence record."""
    metrics = " ".join(f'{m["value"]} {m["meaning"]}' for m in ev.get("metrics", []))
    return " ".join([ev.get("result", ""), ev.get("how", ""), metrics, " ; ".join(ev.get("skills", [])), ev.get("raw_notes", "")])


def numbers(text):
    """Normalised numbers that appear in text."""
    return {n.replace(",", "") for n in NUMBER.findall(clean(text))}


def month_index(value, today):
    """Months since year 0 for 'YYYY-MM', or for today when 'present'."""
    if not value or value == "present":
        return today.year * 12 + today.month - 1
    year, month = value.split("-")[:2]
    return int(year) * 12 + int(month) - 1


def experience_years(profile, today):
    """Whole years of work experience, with overlapping or back-to-back roles merged."""
    spans = sorted((month_index(w["start"], today), month_index(w.get("end"), today)) for w in profile.get("work", []))
    merged = []
    for start, end in spans:
        if merged and start <= merged[-1][1] + 1:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    return sum(end - start + 1 for start, end in merged) // 12


def page_limit(profile, config, today):
    """Page limit from preferences, or from years of experience."""
    pref = profile.get("preferences", {}).get("page_limit", "auto")
    if pref != "auto":
        return int(pref)
    return 2 if experience_years(profile, today) >= config["length"]["two_page_years"] else 1


def bullets(resume):
    """(owner ID, label, bullet) for every work and project bullet."""
    out = []
    for key, id_key in (("work", "role_id"), ("projects", "project_id")):
        for item in resume.get(key, []):
            out += [(item[id_key], f"{item[id_key]}#{i}", b) for i, b in enumerate(item["bullets"], 1)]
    return out


def prose(resume):
    """Tagline, summary and bullets: the text keyword use is judged on."""
    return clean("\n".join([resume.get("tagline", ""), resume.get("summary", ""), *(b["text"] for _, _, b in bullets(resume))]))


def fix(rule, text, fixable=True, points=0.0):
    """One suggestion for the next revision."""
    return {"rule": rule, "fix": text, "fixable": fixable, "points": round(points, 1)}


def keyword_table(analysis, profile, rules, config):
    """Weight, matcher and profile support for every job keyword."""
    kw = config["keywords"]
    ev_texts = {i: clean(evidence_text(ev)) for i, (_, ev) in evidence_index(profile).items()}
    roles = [f'{w["title"]} {w.get("summary", "")}' for w in profile.get("work", [])]
    context = clean("\n".join([*ev_texts.values(), *roles]))
    skills = clean(" ; ".join(n for s in profile.get("skills", []) for n in [s["name"], *s.get("aliases", [])]))
    table = []
    for k in analysis["keywords"]:
        rx = keyword_regex(variants(k["term"], k.get("aliases", []), rules["groups"]))
        support = 1.0 if rx.search(context) else kw["skills_only_credit"] if rx.search(skills) else 0.0
        table.append({
            "term": k["term"],
            "importance": k["importance"],
            "weight": kw["required_weight"] if k["importance"] == "required" else kw["preferred_weight"],
            "rx": rx,
            "support": support,
            "evidence": [i for i, text in ev_texts.items() if rx.search(text)],
        })
    return table


def ceiling(table, config):
    """Best score the profile can reach for this job, and the loop target."""
    weights = config["score"]["weights"]
    total = sum(k["weight"] for k in table) or 1
    coverage = sum(k["weight"] * k["support"] for k in table) / total
    best = round(weights["keywords"] * coverage + sum(v for name, v in weights.items() if name != "keywords"), 1)
    return best, min(config["score"]["threshold"], round(best - config["score"]["ceiling_margin"], 1))


def fact_mismatches(resume, profile):
    """Employers, titles, dates, degrees and certificates that differ from the profile."""
    out = []
    roles = {w["id"]: w for w in profile.get("work", [])}
    for w in resume.get("work", []):
        src = roles.get(w["role_id"])
        if not src:
            out.append(f'role {w["role_id"]} is not in the profile')
            continue
        fields = ["company", "title", "start", "end"] + (["location"] if w.get("location") else [])
        out += [f'{w["role_id"]}.{f} is "{w.get(f)}" but the profile says "{src.get(f)}"' for f in fields if w.get(f) != src.get(f)]
    projects = {p["id"]: p for p in profile.get("projects", [])}
    for p in resume.get("projects", []):
        src = projects.get(p["project_id"])
        if not src or p["name"] != src["name"]:
            out.append(f'project {p["project_id"]} does not match the profile')
    schools = {(e["institution"], e["degree"]): e for e in profile.get("education", [])}
    for e in resume.get("education", []):
        src = schools.get((e["institution"], e["degree"]))
        if not src or any(e.get(f) and e[f] != src.get(f) for f in ("field", "grade", "start", "end")):
            out.append(f'education "{e["degree"]}, {e["institution"]}" does not match the profile')
    certs = {c["name"] for c in profile.get("certificates", [])}
    out += [f'certificate "{c["name"]}" is not in the profile' for c in resume.get("certificates", []) if c["name"] not in certs]
    return out


def gates(resume, profile, pdf, rules, limit, today):
    """Hard checks; any failure means the résumé can't be used."""
    index = evidence_index(profile)
    fails = {rule: [] for rule in ("EVD-02", "EVD-03", "EVD-04", "EVD-05", "SKL-02", "FMT-04", "LEN-01")}
    for owner, label, b in bullets(resume):
        wrong = [c for c in b["evidence_ids"] if c not in index or index[c][0] != owner]
        if wrong or not b["evidence_ids"]:
            fails["EVD-02"].append(f"{label} cites {wrong or 'no evidence'}; cite evidence from {owner}")
            continue
        allowed = set().union(*(numbers(evidence_text(index[c][1])) for c in b["evidence_ids"]))
        extra = numbers(b["text"]) - allowed
        if extra:
            fails["EVD-03"].append(f'{label} uses {sorted(extra)}, which are not in {b["evidence_ids"]}')

    head = f'{resume.get("tagline", "")}\n{resume.get("summary", "")}'
    ids = resume.get("summary_evidence_ids", [])
    unknown = [c for c in ids if c not in index]
    if unknown:
        fails["EVD-02"].append(f"summary cites unknown evidence {unknown}")
    allowed = set().union(*(numbers(evidence_text(index[c][1])) for c in ids if c in index))
    allowed |= {n for n in YEARS.findall(head) if int(n) <= experience_years(profile, today)}
    extra = numbers(head) - allowed
    if extra:
        fails["EVD-03"].append(f"tagline/summary uses {sorted(extra)}, which are not in summary_evidence_ids")

    fails["EVD-04"] += fact_mismatches(resume, profile)
    known = {v.lower() for s in profile.get("skills", []) for v in variants(s["name"], s.get("aliases", []), rules["groups"])}
    fails["SKL-02"] += [f"{item} is not in the profile" for c in resume.get("skills", []) for item in c["items"] if item.lower() not in known]
    rendered = [
        resume.get("tagline", ""),
        resume.get("summary", ""),
        *(b["text"] for _, _, b in bullets(resume)),
        *(item for c in resume.get("skills", []) for item in c["items"]),
    ]
    fails["EVD-05"] += [f"placeholder in: {t[:60]}" for t in rendered if PLACEHOLDER.search(t)]
    if len(pdf["text"].strip()) < 200:
        fails["FMT-04"].append("the PDF has little or no extractable text")
    if pdf["pages"] > limit:
        fails["LEN-01"].append(f'{pdf["pages"]} pages but the limit is {limit}; cut the oldest, least relevant bullets (LEN-03)')
    return [{"rule": rule, "ok": not detail, "detail": detail} for rule, detail in fails.items()]


def keyword_part(resume, table, config):
    """Keyword coverage: full credit in context, partial in Skills only, minus repetition."""
    kw, weight = config["keywords"], config["score"]["weights"]["keywords"]
    text = prose(resume)
    skills = clean(" ; ".join(item for c in resume.get("skills", []) for item in c["items"]))
    total = sum(k["weight"] for k in table) or 1
    got, terms, fixes = 0.0, [], []
    for k in table:
        uses = len(k["rx"].findall(text))
        credit = 1.0 if uses else kw["skills_only_credit"] if k["rx"].search(skills) else 0.0
        got += k["weight"] * credit
        terms.append({"term": k["term"], "importance": k["importance"], "credit": credit, "uses": uses})
        gain = weight * k["weight"] * (k["support"] - credit) / total
        if uses > kw["max_repeats"]:
            fixes.append(fix("KW-03", f'"{k["term"]}" is used {uses} times in the tagline, summary and bullets; keep it to {kw["max_repeats"]}.', True, kw["repeat_penalty"]))
        elif gain > 0 and k["support"] == 1.0:
            backing = ", ".join(k["evidence"][:3]) or "your role titles"
            fixes.append(fix("KW-04", f'{k["importance"].capitalize()} keyword "{k["term"]}" is backed by {backing} but not used in a bullet or the summary.', True, gain))
        elif gain > 0:
            fixes.append(fix("KW-04", f'Add "{k["term"]}" to the Skills section; it is in your profile skills.', True, gain))
    over = sum(1 for t in terms if t["uses"] > kw["max_repeats"])
    return {"points": max(0.0, weight * got / total - kw["repeat_penalty"] * over), "terms": terms}, fixes


def impact_part(resume, profile, config):
    """Share of bullets that carry a number."""
    weight, target = config["score"]["weights"]["impact"], config["bullets"]["quantified_target"]
    index = evidence_index(profile)
    items = bullets(resume)
    missing = [(label, b) for _, label, b in items if not (numbers(b["text"]) or QUANT_WORDS.search(b["text"]))]
    ratio = 1 - len(missing) / len(items) if items else 0.0
    fixes = []
    if ratio < target:
        each = weight / target / len(items)
        for label, b in missing:
            metrics = [m["value"] for c in b["evidence_ids"] if c in index for m in index[c][1].get("metrics", [])]
            if metrics:
                fixes.append(fix("BUL-04", f'{label} has no number; its evidence has: {"; ".join(metrics)}.', True, each))
            else:
                fixes.append(fix("BUL-04", f"{label} has no number and its evidence has none; ask the user for one next time.", False))
    return {"points": weight * min(1.0, ratio / target), "quantified": round(ratio, 2)}, fixes


def banned_in(text, rules):
    """First banned phrase found in text, or ''."""
    low = clean(text).lower()
    return next((p for p in rules["banned"] if re.search(rf"(?<![a-z]){re.escape(p)}(?![a-z])", low)), "")


def bullet_part(resume, rules, config):
    """Action verbs, length, clichés, pronouns and verb variety."""
    cfg, weight = config["bullets"], config["score"]["weights"]["bullets"]
    checks, verbs = [], []
    for _, label, b in bullets(resume):
        text = b["text"].strip()
        first = re.sub(r"[^a-z-]", "", text.split()[0].lower()) if text else ""
        verbs.append(first)
        phrase = banned_in(text, rules)
        checks += [
            ("BUL-02", first in rules["verbs"], f'{label} should start with a past-tense action verb, not "{first}".'),
            ("BUL-03", len(text) <= cfg["max_chars"], f'{label} is {len(text)} characters; keep it to {cfg["max_chars"]}.'),
            ("SUM-04", not phrase, f'{label} uses the cliché "{phrase}".'),
            ("BUL-08", not PRONOUN.search(text), f"{label} uses a first-person pronoun."),
        ]
    for label in ("tagline", "summary"):
        text = resume.get(label, "")
        phrase = banned_in(text, rules)
        checks += [
            ("SUM-04", not phrase, f'The {label} uses the cliché "{phrase}".'),
            ("SUM-02", not PRONOUN.search(text), f"The {label} uses a first-person pronoun."),
        ]
    each = weight / len(checks)
    fixes = [fix(rule, msg, True, each) for rule, ok, msg in checks if not ok]
    repeated = {v: n for v, n in Counter(verbs).items() if n > cfg["max_verb_repeats"]}
    fixes += [fix("BUL-07", f'"{v}" starts {n} bullets; use it at most {cfg["max_verb_repeats"]} times.', True, 1) for v, n in repeated.items()]
    points = weight * sum(ok for _, ok, _ in checks) / len(checks) - len(repeated)
    return {"points": max(0.0, points)}, fixes


def parse_part(resume, pdf, config):
    """What an ATS can read back from the rendered PDF."""
    weight = config["score"]["weights"]["parse"]
    raw, flat = pdf["text"], squash(pdf["text"])
    lines = [re.sub(r"\s+", "", line).upper() for line in raw.splitlines()]
    items = bullets(resume)
    found = sum(squash(b["text"]) in flat for _, _, b in items)
    position, headings_ok = 0, True
    for key in section_order(resume):
        try:
            position = lines.index(HEADINGS[key].upper(), position) + 1
        except ValueError:
            headings_ok = False
            break
    basics = resume["basics"]
    contact_ok = all(squash(basics[k]) in flat for k in ("email", "linkedin") if basics.get(k))
    if basics.get("phone"):
        contact_ok = contact_ok and re.sub(r"\D", "", basics["phone"]) in re.sub(r"\D", "", raw)
    data = display_data(resume, config)
    dates = [e["dates"] for key in ("experience", "projects", "education") for e in data[key] if e["dates"]]
    checks = [
        (6, found / len(items) if items else 1.0, "FMT-04", f"{len(items) - found} bullet(s) can't be found in the PDF text."),
        (4, headings_ok, "FMT-02", "Section headings are missing or out of order in the PDF text."),
        (4, contact_ok, "FMT-08", "Email, phone or LinkedIn can't be read from the PDF text."),
        (2, all(squash(d) in flat for d in dates), "FMT-05", "Some dates can't be read from the PDF text."),
        (2, not LIGATURE.search(raw), "FMT-06", "The PDF text contains ligature or private-use characters."),
        (2, pdf["mb"] <= config["pdf"]["max_mb"], "FMT-04", f'The PDF is {pdf["mb"]:.2f} MB; keep it under {config["pdf"]["max_mb"]} MB.'),
    ]
    scale = weight / sum(w for w, *_ in checks)
    fixes = [fix(rule, msg, False, w * scale * (1 - float(ok))) for w, ok, rule, msg in checks if float(ok) < 1]
    return {"points": scale * sum(w * float(ok) for w, ok, *_ in checks)}, fixes


def fit_part(resume, analysis, table, config):
    """Job-title words and the top required keywords in the tagline or summary."""
    weight = config["score"]["weights"]["fit"]
    head = clean(f'{resume.get("tagline", "")}\n{resume.get("summary", "")}')
    words = [w for w in re.findall(r"[a-z0-9+#]+", clean(analysis["job"]["title"]).lower()) if w not in TITLE_NOISE]
    missing_words = [w for w in words if not re.search(rf"(?<![a-z0-9]){re.escape(w)}s?(?![a-z0-9])", head.lower())]
    top = [k for k in [k for k in table if k["importance"] == "required"][:3] if k["support"] == 1.0]
    missing_top = [k["term"] for k in top if not k["rx"].search(head)]
    title_share = 1 - len(missing_words) / len(words) if words else 1.0
    top_share = 1 - len(missing_top) / len(top) if top else 1.0
    fixes = []
    if missing_words:
        fixes.append(fix("SUM-03", f"Use the job-title words {missing_words} in the tagline or summary.", True, weight / 2 * (1 - title_share)))
    if missing_top:
        fixes.append(fix("SUM-03", f"Mention {missing_top} in the tagline or summary.", True, weight / 2 * (1 - top_share)))
    return {"points": weight * (title_share + top_share) / 2}, fixes


def score(resume, analysis, profile, pdf, config, rules, today=None):
    """Full score report for one résumé version."""
    today = today or date.today()
    table = keyword_table(analysis, profile, rules, config)
    best, target = ceiling(table, config)
    limit = page_limit(profile, config, today)
    gate_list = gates(resume, profile, pdf, rules, limit, today)
    results = {
        "keywords": keyword_part(resume, table, config),
        "impact": impact_part(resume, profile, config),
        "bullets": bullet_part(resume, rules, config),
        "parse": parse_part(resume, pdf, config),
        "fit": fit_part(resume, analysis, table, config),
    }
    weights = config["score"]["weights"]
    total = round(sum(part["points"] for part, _ in results.values()), 1)
    part_fixes = sorted((f for _, fs in results.values() for f in fs), key=lambda f: (not f["fixable"], -f["points"]))
    return {
        "version": resume.get("version"),
        "passed": all(g["ok"] for g in gate_list) and total >= target,
        "score": total,
        "target": target,
        "ceiling": best,
        "pages": pdf["pages"],
        "page_limit": limit,
        "gates": gate_list,
        "parts": {name: {**part, "points": round(part["points"], 1), "max": weights[name]} for name, (part, _) in results.items()},
        "gaps": [k["term"] for k in table if k["support"] == 0],
        "fixes": [fix(g["rule"], d) for g in gate_list for d in g["detail"]] + part_fixes,
    }


def pdf_facts(path):
    """Text, page count and size of a rendered PDF."""
    from pypdf import PdfReader

    reader = PdfReader(str(path))
    return {
        "text": "\n".join(page.extract_text() or "" for page in reader.pages),
        "pages": len(reader.pages),
        "mb": Path(path).stat().st_size / 1_048_576,
    }


def main():
    """CLI: `ceiling <job_dir>` or `score <job_dir> <N>`."""
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--profile", default=str(ROOT / "profile" / "profile.json"))
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("ceiling", parents=[common]).add_argument("job_dir")
    score_cmd = sub.add_parser("score", parents=[common])
    score_cmd.add_argument("job_dir")
    score_cmd.add_argument("version", type=int)
    args = parser.parse_args()

    config, rules = load_config(), load_rules()
    job, profile = Path(args.job_dir), load_json(args.profile)
    analysis = load_json(job / "analysis.json")
    if args.command == "ceiling":
        table = keyword_table(analysis, profile, rules, config)
        best, target = ceiling(table, config)
        print(json.dumps({
            "ceiling": best,
            "target": target,
            "stretch": best < config["score"]["threshold"],
            "page_limit": page_limit(profile, config, date.today()),
            "gaps": [{"term": k["term"], "importance": k["importance"]} for k in table if k["support"] == 0],
            "skills_list_only": [k["term"] for k in table if 0 < k["support"] < 1],
        }, indent=2, ensure_ascii=False))
        return

    n = args.version
    report = score(load_json(job / f"resume.v{n}.json"), analysis, profile, pdf_facts(job / f"resume.v{n}.pdf"), config, rules)
    (job / f"score.v{n}.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    failed = [g["rule"] for g in report["gates"] if not g["ok"]]
    print(
        f'v{n}: {report["score"]}/100, target {report["target"]}, ceiling {report["ceiling"]}; '
        f'failed gates: {", ".join(failed) or "none"}; fixes: {len(report["fixes"])}; passed: {report["passed"]}'
    )


if __name__ == "__main__":
    main()
