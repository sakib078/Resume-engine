---
name: analyze-job
description: Turn jobs/<slug>/jd.md (job description and company brief) into analysis.json, covering the employer's problems, weighted keywords with aliases, duties and company context. Step 1 of tailor-resume.
---

# Analyse a job

Read `jobs/<slug>/jd.md` and the KW rules in `rules/resume-rules.md`. Use only what the job description and brief say; don't infer.

1. **Problems (KW-01):** the 3–5 things this role must solve, most important first. IDs `P1`–`P5`, each with a short quote from the JD in `evidence_in_jd`.
2. **Keywords:** 10–30 hard skills, tools, methods, domain terms, soft skills and certifications the employer asks for.
   - `term`: exactly as the JD writes it.
   - `importance`: `required` (must-have, essential, listed as a requirement) or `preferred` (nice to have, desirable, bonus, ideally).
   - `category`: technical, tool, domain, methodology, soft_skill, certification or other.
   - `aliases`: other names for the same thing: acronym and full name, UK and US spelling, JD synonyms.
   - Order: required first, most important first. The first 3 required keywords drive the fit score.
   - Leave out generic words (data, team, experience). Keep a soft skill only when it's specific ("data storytelling").
   - Cross-check `rules/lexicon.json`: every lexicon term or alias that appears in the JD must be on your list.
3. **Job:** the exact title, plus seniority, location, employment type, `years_required` (or null) and `spelling` (`en-GB` if the JD uses -ise/-our/-lling spellings, otherwise `en-US`).
4. **Company:** the name, plus industry, stage, size, product, values and tech stack where the brief states them.
5. **Duties:** up to 8 main responsibilities, kept short.
6. Write `jobs/<slug>/analysis.json` and run `PY scripts/validate.py analysis jobs/<slug>/analysis.json`. Fix it until it prints OK.

Shape (full example: `tests/fixtures/analysis.json`):
```json
{
  "job": {"title": "Data Analyst", "seniority": "mid", "location": "Manchester, UK (hybrid)", "years_required": null, "spelling": "en-GB"},
  "company": {"name": "Northwind Logistics", "industry": "Logistics", "tech_stack": ["Snowflake", "dbt"]},
  "problems": [{"id": "P1", "problem": "Operational reporting is slow and manual", "evidence_in_jd": "replace manual weekly reporting with self-serve dashboards"}],
  "keywords": [{"term": "SQL", "importance": "required", "category": "technical", "aliases": []}],
  "duties": ["Build and maintain Power BI dashboards for operations and finance"]
}
```
