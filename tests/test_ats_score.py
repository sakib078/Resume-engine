"""Tests for the deterministic ATS scorer."""
import copy
import json

import pytest

import ats_score


def run(resume, analysis, profile, config, rules, make_pdf):
    """Score a résumé against the fixtures using fake PDF text."""
    return ats_score.score(resume, analysis, profile, make_pdf(resume), config, rules)


def gate(report, rule):
    """The gate entry for one rule."""
    return next(g for g in report["gates"] if g["rule"] == rule)


def test_clean_resume_passes(resume, analysis, profile, config, rules, make_pdf):
    report = run(resume, analysis, profile, config, rules, make_pdf)
    assert all(g["ok"] for g in report["gates"]), report["gates"]
    assert report["passed"], report["fixes"]


def test_invented_number_fails_gate(resume, analysis, profile, config, rules, make_pdf):
    bad = copy.deepcopy(resume)
    bad["work"][0]["bullets"][1]["text"] = (
        "Reduced failed nightly data loads by 90% by moving 14 ETL jobs from cron scripts to Airflow with retries and Slack alerting."
    )
    report = run(bad, analysis, profile, config, rules, make_pdf)
    assert not gate(report, "EVD-03")["ok"]
    assert not report["passed"]


def test_placeholder_fails_gate(resume, analysis, profile, config, rules, make_pdf):
    bad = copy.deepcopy(resume)
    bad["work"][0]["bullets"][3]["text"] += " Saved [X] hours a month."
    report = run(bad, analysis, profile, config, rules, make_pdf)
    assert not gate(report, "EVD-05")["ok"]
    assert not report["passed"]


def test_evidence_from_another_role_fails_gate(resume, analysis, profile, config, rules, make_pdf):
    bad = copy.deepcopy(resume)
    bad["work"][1]["bullets"][1]["evidence_ids"] = ["brightcart-01"]
    report = run(bad, analysis, profile, config, rules, make_pdf)
    assert not gate(report, "EVD-02")["ok"]


def test_repeated_keyword_loses_points(resume, analysis, profile, config, rules, make_pdf):
    clean = run(resume, analysis, profile, config, rules, make_pdf)
    stuffed = copy.deepcopy(resume)
    for bullet in stuffed["work"][0]["bullets"][1:4]:
        bullet["text"] = bullet["text"].rstrip(".") + " in Power BI."
    report = run(stuffed, analysis, profile, config, rules, make_pdf)
    assert report["parts"]["keywords"]["points"] < clean["parts"]["keywords"]["points"]
    assert any(f["rule"] == "KW-03" for f in report["fixes"])


def test_skills_only_keyword_gets_half_credit(resume, analysis, profile, config, rules, make_pdf):
    edited = copy.deepcopy(resume)
    edited["work"][0]["bullets"][1]["text"] = (
        "Reduced failed nightly data loads from 9 a month to 1 by moving 14 ETL jobs from cron scripts to a scheduler with retries and alerting."
    )
    report = run(edited, analysis, profile, config, rules, make_pdf)
    airflow = next(t for t in report["parts"]["keywords"]["terms"] if t["term"] == "Airflow")
    assert airflow["credit"] == 0.5
    assert any(f["rule"] == "KW-04" and "Airflow" in f["fix"] for f in report["fixes"])


def test_ceiling_counts_only_supported_keywords(analysis, profile, config, rules):
    table = ats_score.keyword_table(analysis, profile, rules, config)
    best, target = ats_score.ceiling(table, config)
    assert [k["term"] for k in table if k["support"] == 0] == ["Looker"]
    assert best == 97.5
    assert target == config["score"]["threshold"]


def test_rendered_pdf_reads_back_cleanly(tmp_path, resume, analysis, profile, config, rules):
    pytest.importorskip("typst")
    pytest.importorskip("pypdf")
    import render

    source = tmp_path / "resume.v1.json"
    source.write_text(json.dumps(resume, ensure_ascii=False), encoding="utf-8")
    render.render(source, tmp_path / "resume.v1.pdf", config)
    pdf = ats_score.pdf_facts(tmp_path / "resume.v1.pdf")
    report = ats_score.score(resume, analysis, profile, pdf, config, rules)
    assert pdf["pages"] == 1
    assert all(g["ok"] for g in report["gates"]), report["gates"]
    assert report["parts"]["parse"]["points"] == report["parts"]["parse"]["max"], report["fixes"]
