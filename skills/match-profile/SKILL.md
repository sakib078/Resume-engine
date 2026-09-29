---
name: match-profile
description: Map profile/profile.json against a job's analysis.json and write match.json, covering evidence for each requirement, gaps, what to include, skills to list and questions for the user. Step 2 of tailor-resume.
---

# Match the profile to the job

Read `jobs/<slug>/analysis.json`, `profile/profile.json` and the EVD, KW, LEN and AI rules in `rules/resume-rules.md`.

1. **Requirements:** for every keyword, find evidence that really shows it.
   - `strong`: the evidence names it or clearly demonstrates it.
   - `partial`: related or transferable; say why in `note`.
   - `none`: nothing supports it.

   Cite the evidence IDs. Don't stretch: if the user would struggle to defend it in an interview, it's `partial` or `none`.
2. **Problems:** for each problem (`P1`–`P5`), the evidence that best answers it, plus a one-sentence `angle`.
3. **Gaps (KW-06):** every keyword with strength `none`, with its importance and a short note. Never propose adding them.
4. **Selected:** for every role in the profile (reverse chronological), the evidence IDs to use, most relevant first: 4–6 for recent or relevant roles, 1–3 for older ones (LEN-03). Add projects that cover a required keyword or show AI work (AI-01, AI-03). Evidence IDs must belong to that role or project.
5. **Skills:** profile skill names to list, most relevant first, 48 at most (SKL-01, SKL-02).
6. **Questions (EVD-06, BUL-04), at most 5:** only where the answer would clearly improve a selected bullet. This is usually a missing metric on highly relevant evidence ("Roughly how many hours a week did that save?") or an unclear fact. Link each question to its `evidence_id`.
7. **fit_summary:** 2–3 honest sentences.
8. Write `jobs/<slug>/match.json` and run `PY scripts/validate.py match jobs/<slug>/match.json --profile profile/profile.json`. Fix it until it prints OK.
