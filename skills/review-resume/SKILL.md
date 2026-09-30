---
name: review-resume
description: Review one résumé version as a tech recruiter and as a copywriter, and write review.vN.json with major and minor issues keyed to rule IDs. Step 4 of tailor-resume.
---

# Review a résumé version

Read `jobs/<slug>/resume.vN.json`, `jobs/<slug>/analysis.json`, `profile/profile.json` and `rules/resume-rules.md`. `ats_score.py` already checks numbers, verbs, length, keyword counts and parsing, so don't repeat those checks.

**Recruiter** (the optimiser's tech and data recruiter):
- Is each of P1–P3 answered convincingly in the headline, the summary (if there is one) or the top bullets of the most recent role?
- Is the positioning right for the title and seniority? Would you shortlist this person?

**Copywriter** (the optimiser's expert copywriter, plus Jeff Su's Rule 3):
- Is the text natural and specific, something the user could explain in an interview (BUL-06)?
- Look for generic AI wording (SUM-04), keywords squeezed in awkwardly (KW-02), repetition, and a voice that shifts between sections.

**Severity:**
- `major`: a top-3 problem goes unanswered although the profile has evidence for it; misleading positioning; wording that misstates the evidence; a generic or robotic summary.
- `minor`: everything else.

Suggestions must stay within the evidence.

Write `jobs/<slug>/review.vN.json`, then run `PY scripts/validate.py review jobs/<slug>/review.vN.json`:
```json
{"version": 1,
 "recruiter": {"rating": 4, "shortlist": true, "comment": "..."},
 "copywriter": {"rating": 4, "comment": "..."},
 "issues": [{"severity": "minor", "lens": "copywriter", "rule": "BUL-06", "where": "brightcart#2", "issue": "...", "suggestion": "..."}]}
```
`where` is `tagline`, `summary`, `skills`, or `<role_id or project_id>#<bullet number>`.
