---
name: tailor-resume
description: Build a tailored, ATS-checked résumé PDF for one job from a job description, a company brief and profile/profile.json. Use when the user shares a job posting or asks to tailor their résumé or CV for a role.
---

# Tailor a résumé

Run from `resume-engine/`. `PY` is defined in `AGENTS.md`. If a step fails twice, stop and tell the user what failed.

## 0. Set up the job
1. `profile/profile.json` must pass `PY scripts/validate.py profile profile/profile.json`. If it's missing or invalid, run `skills/build-profile/SKILL.md` first.
2. Job folder: use the one the user names. Otherwise create `jobs/<YYYY-MM-DD>-<company>-<role>/` (lowercase, hyphens) and write `jd.md` from `templates/jd-template.md`: fill in the frontmatter (today's date) and paste the job description and company brief under their headings.
3. Read `threshold`, `max_rounds` and `min_gain` from `config.toml`.

## 1. Analyse the job
Follow `skills/analyze-job/SKILL.md` → `analysis.json`.

## 2. Match the profile
Follow `skills/match-profile/SKILL.md` → `match.json`. Then run `PY scripts/ats_score.py ceiling <job_dir>`.

## 3. Checkpoint 1: ask the user, then wait
Show, briefly:
- `fit_summary`, the ceiling and the target. If `stretch` is true, say the role is a stretch.
- Gaps, required ones first. Say they won't be added.
- The questions from `match.json`.

Ask the user to answer (or skip) the questions and to confirm you should continue. Then:
- Save each answer, exactly as given, into the matching evidence in `profile/profile.json` (`metrics` or `raw_notes`) and re-validate the profile.
- Update `match.json` if the answers change it.

## 4. Write, render, score and review (up to `max_rounds`)
For N = 1, 2, …:
1. Follow `skills/write-resume/SKILL.md` → `resume.vN.json` (revise mode when N > 1).
2. `PY scripts/validate.py resume <job_dir>/resume.vN.json --profile profile/profile.json`
3. `PY scripts/render.py <job_dir>/resume.vN.json <job_dir>/resume.vN.pdf`
4. `PY scripts/ats_score.py score <job_dir> N` → `score.vN.json`
5. Follow `skills/review-resume/SKILL.md` → `review.vN.json`
6. Stop when `score.vN.json` has `"passed": true` and the review has no `major` issues. Also stop at `max_rounds`, or when N > 1 and the score rose by less than `min_gain`.

Pick the best version: all gates passed, then the highest score. If no version passes the gates, don't finalise; show the failed gates and stop.

## 5. Checkpoint 2: finalise
`PY scripts/finalize.py <job_dir> <best N>` → the final PDF and `report.md`.

Tell the user the PDF path, the score against the target, and any open review notes. Ask them to check the "Check every bullet against its evidence" table in `report.md` before applying.
