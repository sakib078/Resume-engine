"""Shared fixtures for the scorer tests."""
import json
from pathlib import Path

import pytest

import ats_score
import render

FIXTURES = Path(__file__).resolve().parent / "fixtures"


def load(name):
    """Read a fixture JSON file."""
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


@pytest.fixture
def config():
    """Engine config."""
    return render.load_config()


@pytest.fixture
def rules():
    """Lexicon, action verbs and banned phrases."""
    return ats_score.load_rules()


@pytest.fixture
def profile():
    """Fictional master profile."""
    return load("profile.json")


@pytest.fixture
def analysis():
    """Analysis of the fictional Northwind job."""
    return load("analysis.json")


@pytest.fixture
def resume():
    """Clean tailored résumé for the Northwind job."""
    return load("resume.sample.json")


@pytest.fixture
def make_pdf(config):
    """Build fake PDF facts that read like pypdf output of the rendered résumé."""
    def build(resume):
        data = render.display_data(resume, config)
        lines = [data["name"], data["tagline"], "  |  ".join(data["contact"])]
        for key in data["order"]:
            lines.append(render.HEADINGS[key].upper())
            if key == "summary":
                lines.append(data["summary"])
            elif key in ("skills", "achievements"):
                lines += [f'{s["category"]}: {", ".join(s["items"])}' for s in data[key]]
            elif key == "certifications":
                lines += data["certifications"]
            else:
                for e in data[key]:
                    lines += [f'{e["title"]} {e["dates"]}', e["sub"], *e["bullets"]]
        return {"text": "\n".join(lines), "pages": 1, "mb": 0.05}

    return build
