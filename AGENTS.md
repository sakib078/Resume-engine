# Resume Engine

Tailors a résumé to one job. Input: a job description + company brief (`jobs/<slug>/jd.md`) and your profile (`profile/profile.json`). Output: an ATS-checked PDF and `report.md`.

## Harness contract
- Works with any agent that can read and write files here and run Python. No hooks, subagents or MCP.
- Run everything from this folder (`resume-engine/`).
- `PY` below means `.venv/Scripts/python.exe` on Windows and `.venv/bin/python` elsewhere.
- Setup once (Python 3.11+): `python -m venv .venv`, then `PY -m pip install -r requirements.txt`.

## Skills: open the file and follow it
| When the user wants to… | Skill |
|---|---|
| Tailor a résumé to a job (default entry point) | `skills/tailor-resume/SKILL.md` |
| Create or update the profile, import an old CV or LinkedIn PDF | `skills/build-profile/SKILL.md` |
| Only analyse a job description | `skills/analyze-job/SKILL.md` |
| Only map the profile to a job | `skills/match-profile/SKILL.md` |
| Only write or revise a résumé version | `skills/write-resume/SKILL.md` |
| Only review a résumé version | `skills/review-resume/SKILL.md` |

## Scripts
```
PY scripts/validate.py <profile|analysis|match|resume|review> <file.json> [--profile profile/profile.json]
PY scripts/render.py <resume.vN.json> <resume.vN.pdf>
PY scripts/ats_score.py ceiling <job_dir>
PY scripts/ats_score.py score <job_dir> <N>
PY scripts/finalize.py <job_dir> <N>
PY scripts/pdf_text.py <file.pdf>
PY -m pytest
```
`pdf_text.py` prints what an ATS reads from a PDF.

## Hard rules
- Never invent facts, numbers, tools, titles or dates. `profile/profile.json` is the only source of truth; gaps are reported, never filled.
- Rules live in `rules/resume-rules.md`; cite rule IDs. Scoring settings live in `config.toml`.
- Every JSON a model writes must pass `validate.py` before the next step.
- Only write inside this folder. `../Resume_cv optimizer workflows/` is read-only source material.
- Don't skip the two user checkpoints in `tailor-resume`.

## Layout
- `rules/`: rulebook, bullet examples, action verbs, banned phrases, keyword lexicon
- `schemas/`: JSON contracts for every artifact
- `scripts/`: validate, render, score, finalize
- `templates/`: `harvard.typ` (PDF layout), `jd-template.md` (new job note)
- `profile/profile.json`: your master profile
- `jobs/<YYYY-MM-DD>-<company>-<role>/`: one folder per application
- `tests/`: scorer tests and fictional fixtures
