import json
import os

from core import paths

# Kept for backwards compatibility with the old bot.py calls.
# New code should use core.content with data/culture.json.

_FILE = paths.data("venda.json")


def _load():
    if not os.path.exists(_FILE):
        return {}
    with open(_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def venda_history():
    d = _load()
    if not d:
        return "History data not found."
    h = d["headers"]
    return "\n".join([
        "Territory:      %s" % h["title"],
        "Location:       %s" % h["location"],
        "Founded as:     %s" % h["founded_as"],
        "Self-governing: %s" % h["declaration_dates"]["self-governing"],
        "Independent:    %s" % h["declaration_dates"]["independent"],
        "First president:%s" % (" " + h["leadership"]["first_president"]),
        "Education:      %s" % h["educational_institution"],
        "",
        d["text"],
    ])


def geography():
    d = _load()
    if not d:
        return "Geography data not found."
    g = d["headers"]["geography"]
    f = d["headers"]["geographical_features"]
    return "\n".join([
        "Territories: %s" % g["territories"],
        "Capital:     %s" % g["capital"],
        "Area:        %s km2" % g["land_area_km2"],
        "Population:  %s (1991 estimate)" % g["population_1991"],
        "Borders:     %s" % ", ".join(g["bordering_states"]),
        "Areas:       %s" % ", ".join(f["areas"]),
        "Wildlife:    %s" % ", ".join(f["wildlife"]),
    ])
