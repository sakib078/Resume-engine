# Résumé Rules

The engine's single rulebook. Skills cite these IDs, and `ats_score.py` reports its fixes by ID. ✓ = checked in code by `ats_score.py`; the rest are applied by the skills and `review-resume`.

## Sources
The originals in `Resume_cv optimizer workflows/` are read-only.
- **[OPT]** `linkedin_optimiser_prompt.json` (the fuller version of the `.md`): the three expert roles, the keyword library and the Harvard résumé spec
- **[JS-G]** `Résumé Guide for the AI Era 5 Research-Backed Rules.md`: Jeff Su's five rules
- **[JS-T]** `AI-Era Résumé Toolkit (Jeff Su).md`: Jeff Su's prompts and bullet examples
- **[ENG]** an engine decision: a resolved conflict or an ATS-safety rule
- `READ ME.docx` only explains how to use the optimiser prompt and adds no rules. Its keyword library lives on in `rules/lexicon.json`.

## EVD: Evidence and honesty
- **EVD-01** Never invent experience, qualifications, achievements, metrics, tools, titles or dates. `profile/profile.json` is the only source of truth. [OPT] [JS-T]
- **EVD-02** ✓ Every bullet cites at least one evidence ID, and every ID comes from the same role or project. [ENG]
- **EVD-03** ✓ Every number in a bullet appears in the evidence it cites. Numbers in the tagline or summary must be in `summary_evidence_ids`, apart from years of experience the profile supports. Derived figures (such as a % worked out from before/after values) count as new: the user must confirm them and add them to the profile first. [ENG]
- **EVD-04** ✓ Employers, job titles, dates, degrees, institutions, certificate names, achievement names and links are copied exactly from the profile. Coursework and achievements can leave items out, but never add new ones. [ENG]
- **EVD-05** ✓ Nothing that gets rendered contains a placeholder (`[X%]`, `[TBD]`, `XX%`). [ENG, resolves OPT]
- **EVD-06** If something important is unclear, ask the user at checkpoint 1 before writing it. [JS-T]

## KW: Keywords and tailoring
- **KW-01** Start from the employer's problems: name the 3–5 things this role must solve before picking keywords. [JS-G] [JS-T]
- **KW-02** Map, don't stuff: only use the job description's wording to describe work the evidence supports. [JS-G] [OPT]
- **KW-03** ✓ Use each keyword at most 3 times across the tagline, summary and bullets. The Skills list doesn't count. [ENG, from JS-G]
- **KW-04** ✓ Show required keywords in context (a bullet or the summary), not only in the Skills list. [JS-G]
- **KW-05** Use the job description's exact spelling of a term at least once ("Power BI", "CI/CD"). When both forms are common, give the full name with the acronym once: "Amazon Web Services (AWS)". [ENG]
- **KW-06** If the profile can't support a requirement, it's a gap: report it, never add it. [JS-T] [OPT]
- **KW-07** Match the job description's spelling (en-GB or en-US) unless `profile.preferences.spelling` is set. [ENG]

## SUM: Tagline and summary
- **SUM-01** Tagline: one line under the name. Give the target role family and 2–3 real strengths as a readable phrase, not a pipe-separated keyword list. [OPT]
- **SUM-02** ✓ Summary: 3–5 sentences in implied first person, with no "I", "me" or "my". [OPT] [ENG]
- **SUM-03** ✓ The tagline plus summary contain the job title's core words and the top 3 required keywords the profile supports. The summary answers the employer's top problems with the strongest evidence. [JS-G] [OPT]
- **SUM-04** ✓ No clichés or generic AI wording (`rules/banned-phrases.txt`). [JS-T]

## BUL: Bullets
- **BUL-01** Google's XYZ formula: accomplished [X] as measured by [Y] by doing [Z]. Lead with the result when there's a metric. [JS-G] [JS-T]
- **BUL-02** ✓ Start with a past-tense action verb from `rules/action-verbs.txt`. [OPT]
- **BUL-03** ✓ One or two lines: 220 characters or fewer. [OPT]
- **BUL-04** ✓ At least 60% of bullets contain a number. Metrics beyond revenue count: time saved, speed, scale, accuracy, volume, adoption. [JS-G] [OPT]
- **BUL-05** Keep every fact, number, responsibility and result from the evidence; only the wording changes. [JS-T] [JS-G]
- **BUL-06** The user must be able to explain every bullet naturally in an interview. No keywords squeezed in awkwardly. [JS-T] [OPT]
- **BUL-07** ✓ No more than 2 bullets start with the same verb. [ENG]
- **BUL-08** ✓ No first-person pronouns. [ENG]
- **BUL-09** If the evidence has no metric, write a concrete bullet (context, then action, then result) without a number. Never use a placeholder. [ENG, resolves OPT vs JS]

## SKL: Skills section
- **SKL-01** At most 8 categories, with 4–6 terms each where the profile allows. [OPT]
- **SKL-02** ✓ List only skills that are in the profile. Order categories and terms by how relevant they are to the job. [OPT] [ENG]
- **SKL-03** If the job uses a different name for one of the profile's skills (a lexicon alias), use the job's name. [ENG]

## AI: AI skills
- **AI-01** If the profile has relevant evidence with `ai_used: true`, include at least one bullet that shows what the AI work achieved, not just which tool was used. [JS-G] [JS-T]
- **AI-02** Link to the proof (portfolio, GitHub, a doc) when the evidence has a link. [JS-G]
- **AI-03** With no workplace AI example, put a relevant independent AI project under PROJECTS. [JS-G]

## FMT: Format and parsing
- **FMT-01** One column. No tables, text boxes, icons, photos, skill bars, colour sidebars or decoration. [OPT] [JS-G]
- **FMT-02** ✓ Standard headings in this order: SUMMARY, SKILLS, EXPERIENCE, PROJECTS, EDUCATION, CERTIFICATIONS, ACHIEVEMENTS. Education goes before Experience only for new graduates. [JS-G] [ENG]
- **FMT-03** Nothing important in the page header or footer. [OPT]
- **FMT-04** ✓ A selectable-text PDF under 2.5 MB, with every bullet readable in the extracted text (Jeff Su's copy-paste test). [JS-G]
- **FMT-05** ✓ Dates as `Mon YYYY – Mon YYYY` or `Mon YYYY – Present`, right-aligned on the role line. [OPT]
- **FMT-06** ✓ Left-aligned text with hyphenation and ligatures turned off, so keywords come out whole when the text is extracted. [ENG, resolves OPT "justified"]
- **FMT-07** Typography: name 22pt bold, centred; headings 10pt bold uppercase, lightly letter-spaced, over a full-width rule; role titles 10.5pt bold; body 10pt serif. [OPT]
- **FMT-08** ✓ Contact line: email | phone | location | LinkedIn (plus website, GitHub and any profile links), centred under the tagline. [OPT] [JS-G]

## LEN: Length and order
- **LEN-01** ✓ One page for under 10 years' experience; two pages at most from 10 years. [OPT]
- **LEN-02** Reverse chronological order. [OPT]
- **LEN-03** 4–6 bullets for recent or relevant roles, 1–3 for older ones. Cut the oldest, least relevant bullets first. [OPT] [ENG]
- **LEN-04** Final file name: `First_Last_Company_Role.pdf`. [ENG]

## Resolved conflicts
| Topic | [OPT] | [JS-G] / [JS-T] | Decision |
|---|---|---|---|
| Bullet formula | CAR/STAR | Google XYZ | XYZ, starting with an action verb (BUL-01, BUL-02); a no-number bullet when there's no metric (BUL-09) |
| Missing metrics | `[X%]` placeholders | Ask first | Ask at checkpoint 1; a placeholder can never reach the PDF (EVD-05) |
| Keyword volume | Up to 50 skills, full gap coverage | Moderate coverage beats maximum; map, don't stuff | Only keywords the evidence supports; 8 × 6 skills at most; each keyword at most 3 times (KW-02, KW-03, SKL-01) |
| Achievements snapshot | 2-column table | One column, no tables | Dropped (FMT-01) |
| Headings | "Core Competencies", "Profile Summary", "Professional Experience" | Standard headings | Summary, Skills, Experience, Projects, Education, Certifications, Achievements (FMT-02) |
| Summary voice | First person | — | Implied first person (SUM-02) |
| Alignment | "Justified paragraphs" | Text must parse cleanly | Left-aligned; hyphenation and ligatures off (FMT-06) |
| LinkedIn-only sections | Photo, banner, featured, recommendations, activity, 220-character headline | — | Dropped; the headline becomes the tagline (SUM-01) |
