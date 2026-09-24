"""Validate the dependency graph and generate KANBAN.md + Trello card descriptions.

Usage: python kanban/generate.py
"""
import json
from pathlib import Path

from board_data import (BOARD_URL, FUNCTIONAL_BOARD_URL, QUESTIONS, SPRINTS,
                        TICKETS, url)

ROOT = Path(__file__).resolve().parent.parent
BY_KEY = {t["key"]: t for t in TICKETS}


def validate():
    for t in TICKETS:
        # "blocks" must be the exact inverse of "blocked_by"
        expected = sorted(o["key"] for o in TICKETS if t["key"] in o["blocked_by"])
        assert sorted(t["blocks"]) == expected, (t["key"], t["blocks"], expected)
        # a ticket is never planned in an earlier sprint than what blocks it
        for dep in t["blocked_by"]:
            assert BY_KEY[dep]["sprint"] <= t["sprint"], (t["key"], dep)
        # a ticket with a dependency is in Blocked (or Backlog), never Ready for Dev
        if t["list"].startswith("✅"):
            assert not t["blocked_by"], t["key"]
    # no dependency cycle
    state = {}

    def visit(k, path=()):
        assert state.get(k) != "visiting", f"cycle: {path + (k,)}"
        if state.get(k) == "done":
            return
        state[k] = "visiting"
        for d in BY_KEY[k]["blocked_by"]:
            visit(d, path + (k,))
        state[k] = "done"

    for t in TICKETS:
        visit(t["key"])


def ref(key):
    if key == "QUESTIONS":
        return f"❓ Client questions {url(key)}"
    return f"{key} {BY_KEY[key]['title']} {url(key)}"


NOTES_ON_TRELLO = {"US-05", "US-07", "US-14"}  # only the notes that change how to work


def trello_desc(t):
    lines = [t["story"], "", f"*{t['epic']} · {t['priority']} · Wireframes: {t['wireframes']}*"]
    if t["blocked_by"]:
        lines += ["", "**⛔ Blocked by:**"] + [f"- {ref(k)}" for k in t["blocked_by"]]
    if t["key"] in NOTES_ON_TRELLO and t["note"]:
        lines += ["", f"ℹ️ {t['note']}"]
    lines += ["", "**🧪 QA – Gherkin scenarios**", "```gherkin", t["gherkin"], "```"]
    return "\n".join(lines)


def markdown():
    out = ["# Learn@Home — Delivery Kanban (User stories)", "",
           f"Trello board: {BOARD_URL}  ",
           f"Functional-block board (deliverable 4): {FUNCTIONAL_BOARD_URL}", "",
           "This document mirrors the Trello board. It is generated from `kanban/board_data.py` "
           "by `python kanban/generate.py`, so the board and this file always say the same thing.", "",
           "## How the board works", "",
           "| List | Meaning |", "|---|---|",
           "| 📘 Read me & Client questions | Legend + questions to validate with Learn@Home |",
           "| Backlog (Should / later) | Priority *Should*: not in the first version unless the client decides otherwise |",
           "| ⛔ Blocked | Tickets waiting for another ticket (see **Blocked by**) |",
           "| ✅ Ready for Dev | Nothing blocks them: the team starts here |",
           "| In Progress / Code Review / QA / Done | Normal flow. QA = Gherkin scenarios automated and green |",
           "", "**Rule:** a ticket moves from *Blocked* to *Ready for Dev* when every ticket in its "
           "*Blocked by* checklist is in *Done*.", "",
           "Labels (colour = functional block): 🟢 Authentication · 🔵 Dashboard · 🟣 Chat · 🟡 Calendar · 🟠 Task management · 🔴 Blocked (EN-01 has no colour)", "",
           "## Dependency graph", "", "```mermaid", "graph LR"]
    for t in TICKETS:
        out.append(f'  {t["key"].replace("-", "")}["{t["key"]}<br/>{t["title"]}"]')
    for t in TICKETS:
        for d in t["blocked_by"]:
            out.append(f'  {d.replace("-", "")} --> {t["key"].replace("-", "")}')
    out += ["```", "", "Arrow `A --> B` = *A blocks B* (B cannot be finished before A).", ""]
    out += ["", "## Summary", "",
            "| Ticket | Title | Block | Priority | List | Blocked by |", "|---|---|---|---|---|---|"]
    for t in sorted(TICKETS, key=lambda t: (t["sprint"], t["key"])):
        out.append(f"| [{t['key']}]({url(t['key'])}) | {t['title']} | {t['epic']} | {t['priority']} | {t['list']} | "
                   f"{', '.join(t['blocked_by']) or '—'} |")
    out += ["", "## Open questions for Learn@Home", ""]
    for q, text, rel in QUESTIONS:
        out.append(f"- **{q}** — {text} *(impacts: {', '.join(rel)})*")
    out += ["", "## Tickets", ""]
    for t in sorted(TICKETS, key=lambda t: (t["sprint"], t["key"])):
        out += [f"### {t['key']} · {t['title']}", "",
                f"**List:** {t['list']} · **Block:** {t['epic']} · "
                f"**Actor:** {t['actor']} · **Priority:** {t['priority']} · **Use case:** {t['uc']} · "
                f"**Wireframes:** {t['wireframes']} · [Trello card]({url(t['key'])})", "",
                f"> {t['story']}", ""]
        if t["blocked_by"]:
            out.append(f"- ⛔ **Blocked by:** {', '.join(t['blocked_by'])}")
        if t["note"]:
            out.append(f"- ℹ️ {t['note']}")
        for name, items in t.get("checklists", {}).items():
            out += ["", f"**{name}**", ""] + [f"- [ ] {a}" for a in items]
        if t["ac"]:
            out += ["", "**Requirements (to do)**", ""] + [f"- [ ] {a}" for a in t["ac"]]
        out += ["", "**Gherkin**", "", "```gherkin", t["gherkin"], "```", ""]
    return "\n".join(out)


if __name__ == "__main__":
    validate()
    (ROOT / "KANBAN.md").write_text(markdown(), encoding="utf-8")
    out = {t["key"]: trello_desc(t) for t in TICKETS}
    (ROOT / "kanban" / "trello_descriptions.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print("OK - dependency graph valid,", len(TICKETS), "tickets")
