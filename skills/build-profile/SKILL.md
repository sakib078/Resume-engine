---
name: build-profile
description: Create or update profile/profile.json, the master career profile, through a brain-dump interview, by importing an old CV or a LinkedIn PDF export, or by saving answers from a tailoring run. Use before the first tailor-resume run and whenever the user has new experience.
---

# Build the profile

`profile/profile.json` is the only source of truth for every résumé. Write only what the user tells you or confirms: never estimate, round up or fill gaps. `tests/fixtures/profile.json` shows the shape. Validate after every change with `PY scripts/validate.py profile profile/profile.json`.

## Modes
- **Interview:** a new profile, or a new role or achievement.
- **Import:** an old CV, a LinkedIn PDF export (LinkedIn → More → Save to PDF) or pasted text. If you can't read PDFs directly, run `PY scripts/pdf_text.py <file.pdf>`. Put what you find into the fields, keeping the original wording in `raw_notes`. Flag any sections that are missing, then go through the metrics questions.
- **Update:** answers from checkpoint 1 of `tailor-resume`. Add each one to the evidence it's about.

## Interview (one role at a time, most recent first)
1. **basics** and **preferences:** target roles, `page_limit` (auto, 1 or 2), `spelling` (auto, en-GB or en-US), `new_grad`.
2. **Role:** `id` (short slug, e.g. `brightcart`), company, title, location, `start`/`end` as `YYYY-MM` (`end` is `present` for the current role).
3. **Brain dump (Jeff Su, Rule 3):** for each achievement ask: What was the final result? What did you specifically do? How did you do it? Keep the answer word for word in `raw_notes`, then fill in `result`, `how`, `skills`, `ai_used` and `link`.
4. **Metrics (Jeff Su, Rule 4):** help the user find the most relevant metric for each achievement. Ask about time saved, speed, scale, volume, accuracy, adoption and money, not just revenue. Record only numbers the user states, in `metrics` as `{value, meaning}`.
5. Evidence IDs: `<role-id>-01`, `<role-id>-02`, …
6. **projects:** especially AI work with links (AI-02, AI-03). Then **education**, **certificates** and **skills** (each with a `category`, plus `aliases` where useful).
7. Show the user a short summary of what you saved and ask them to correct anything that's wrong.
