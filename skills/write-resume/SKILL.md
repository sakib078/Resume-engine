---
name: write-resume
description: Write or revise one tailored résumé version (jobs/<slug>/resume.vN.json) from match.json, profile/profile.json and the rulebook, with every bullet citing its evidence. Step 4 of tailor-resume.
---

# Write a résumé version

Read `jobs/<slug>/analysis.json`, `jobs/<slug>/match.json`, `profile/profile.json`, `rules/resume-rules.md` and `rules/examples.md`.

## New version (N = 1)
1. **basics** and **links:** copy from the profile unchanged. Links go in the header, so keep only the ones worth showing for this job.
2. **work:** for each selected role, in profile order, copy `role_id`, `company`, `title`, `location`, `start` and `end` exactly (EVD-04). Write one bullet per selected evidence item, in the selected order:
   - XYZ, result first when there's a metric (BUL-01). With no metric, write a concrete bullet without a number (BUL-09).
   - Start with a past-tense verb from `rules/action-verbs.txt` (BUL-02). No verb starts more than 2 bullets (BUL-07).
   - 220 characters or fewer (BUL-03). No "I", "me" or "my" (BUL-08).
   - Use only numbers that appear in the cited evidence; no derived figures (EVD-03). No placeholders (EVD-05).
   - Use the job's wording where the evidence supports it (KW-02, KW-04), each keyword at most 3 times across the tagline, summary and bullets (KW-03).
   - Keep every fact. Write something the user could explain in an interview (BUL-05, BUL-06).
   - `evidence_ids`: the evidence the bullet is based on, from this same role.
3. **projects:** the same rules, for the selected projects (AI-01 to AI-03).
4. **tagline (SUM-01)** and **summary (SUM-02 to SUM-04):**
   - Answer P1–P3 with the strongest evidence.
   - Include the job title's core words and the top 3 required keywords the profile supports.
   - Put the evidence behind any number you use in `summary_evidence_ids`. The only exception is years of experience the profile supports.
5. **skills:** up to 8 categories (use the profile's), each with up to 6 items from `match.skills`, most relevant first. If the job names one of your skills differently (a lexicon alias), use the job's name (SKL-01 to SKL-03).
6. **education**, **certificates** and **achievements:** copy from the profile exactly. Set `education_first` to `profile.preferences.new_grad`. For `coursework`, use the profile's course names, most relevant to the job first. Group achievements as `{category, items}` using the profile's `category` and `name`, most relevant first. If the page is full, drop the least relevant courses and achievements before cutting any bullet.
7. **Spelling:** follow `analysis.job.spelling` unless `profile.preferences.spelling` is set (KW-07).
8. **Length:** fit the page limit (LEN-01). Cut the oldest, least relevant bullets first (LEN-03).
9. **changes:** change-log rows `{section, change, why}` saying what you emphasised or left out for this job, and why.
10. Write `jobs/<slug>/resume.v1.json` with `"version": 1`.

## Revision (N > 1)
Start from `resume.v(N-1).json`:
- Apply every fix in `score.v(N-1).json` where `fixable` is true, and every issue in `review.v(N-1).json`.
- Leave lines that aren't mentioned alone.
- Never fix anything by adding content the evidence doesn't support. If a fix can't be made honestly, skip it and add a row to `changes` saying why.
- Save as `resume.vN.json` with `"version": N`, and add rows to `changes`.

Shape of one work entry (full example: `tests/fixtures/resume.sample.json`):
```json
{"role_id": "brightcart", "company": "BrightCart Ltd", "title": "Data Analyst", "location": "Manchester, UK", "start": "2022-03", "end": "present",
 "bullets": [{"text": "Cut weekly sales reporting from 6 hours to 45 minutes by rebuilding 12 Excel reports as one Power BI dashboard on SQL views in Snowflake.", "evidence_ids": ["brightcart-01"]}]}
```
