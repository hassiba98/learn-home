"""Create the Learn@Home Kanban on GitHub: labels, sprint milestones, one issue per
ticket (with dependencies), and a GitHub Projects board with the Kanban columns.

Requirements: GitHub CLI logged in with the project scope:
    gh auth login
    gh auth refresh -s project

Usage (from the repository root):
    python kanban/create_github_issues.py --dry-run   # print what would be created
    python kanban/create_github_issues.py             # create everything
"""
import argparse
import json
import subprocess
import sys

from board_data import QUESTIONS, SPRINTS, TICKETS

OWNER = "hassiba98"
REPO = "learn-home"
PROJECT_TITLE = "Learn@Home - Kanban"
COLUMNS = ["Backlog", "Blocked", "Ready for Dev", "In Progress", "Code Review / QA", "Done"]

LABELS = {
    "Authentication": ("0e8a16", "Functional block: authentication"),
    "Dashboard": ("1d76db", "Functional block: dashboard"),
    "Chat": ("5319e7", "Functional block: chat"),
    "Calendar": ("fbca04", "Functional block: calendar"),
    "Task management": ("d93f0b", "Functional block: task management"),
    "Foundation": ("c5def5", "Enabler needed by several user stories"),
    "Must": ("b60205", "MoSCoW priority: Must"),
    "Should": ("f9d0c4", "MoSCoW priority: Should"),
    "blocked": ("e11d21", "Waiting for another ticket (see Blocked by)"),
    "ready for dev": ("0e8a16", "No open dependency: can be started"),
    "client question": ("d4c5f9", "Question to validate with Learn@Home"),
}

DRY_RUN = False


def gh(*args, stdin=None):
    """Run a gh command and return its stdout."""
    if DRY_RUN:
        print("gh", " ".join(repr(a) if " " in a else a for a in args))
        return ""
    result = subprocess.run(["gh", *args], input=stdin, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"gh {' '.join(args)}\n{result.stderr}")
    return result.stdout.strip()


def column_of(ticket):
    if ticket["list"].startswith("✅"):
        return "Ready for Dev"
    if ticket["list"].startswith("Backlog"):
        return "Backlog"
    return "Blocked"


def issue_body(t, numbers):
    def ref(key):
        if key == "QUESTIONS":
            return f"#{numbers['QUESTIONS']} (client questions)" if "QUESTIONS" in numbers else "client questions"
        return f"#{numbers[key]} {key}" if key in numbers else key

    lines = [f"> {t['story']}", "",
             "| Functional block | Actor | Priority | Use case | Wireframes | Sprint |",
             "|---|---|---|---|---|---|",
             f"| {t['epic']} | {t['actor']} | {t['priority']} | {t['uc']} | {t['wireframes']} | {t['sprint']} |",
             "", "## Dependencies", ""]
    lines.append("**Blocked by:** " + (", ".join(ref(k) for k in t["blocked_by"]) or "none, can start now"))
    lines.append("")
    lines.append("**Blocks:** " + (", ".join(ref(k) for k in t["blocks"]) or "nothing"))
    if t["relates"]:
        lines += ["", "**Related to:** " + ", ".join(ref(k) for k in t["relates"])]
    if t["note"]:
        lines += ["", f"> **Note:** {t['note']}"]
    lines += ["", "## Acceptance criteria", ""] + [f"- [ ] {a}" for a in t["ac"]]
    lines += ["", "## Gherkin scenarios", "", "```gherkin", t["gherkin"], "```", "",
              "## Definition of Done", "",
              "All acceptance criteria checked, Gherkin scenarios automated and green, code reviewed, merged."]
    return "\n".join(lines)


def questions_body(numbers):
    lines = ["Points found while cross-checking the kick-off notes, use cases, user stories and wireframes. "
             "They must be answered before the related tickets are started.", ""]
    for q, text, rel in QUESTIONS:
        refs = ", ".join(f"#{numbers[k]}" if k in numbers else k for k in rel)
        lines.append(f"- [ ] **{q}** — {text} (impacts: {refs})")
    return "\n".join(lines)


def create_issue(title, body, labels, milestone=None):
    args = ["issue", "create", "--repo", f"{OWNER}/{REPO}", "--title", title,
            "--body-file", "-", "--label", ",".join(labels)]
    if milestone:
        args += ["--milestone", milestone]
    url = gh(*args, stdin=body)
    return url, (int(url.rstrip("/").split("/")[-1]) if url else 0)


def main():
    global DRY_RUN
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--no-project", action="store_true", help="only create labels, milestones and issues")
    DRY_RUN = parser.parse_args().dry_run
    no_project = parser.parse_args().no_project
    repo = f"{OWNER}/{REPO}"

    print("1/5 Labels")
    for name, (color, desc) in LABELS.items():
        gh("label", "create", name, "--repo", repo, "--color", color, "--description", desc, "--force")

    print("2/5 Milestones (sprints)")
    for s, goal in SPRINTS.items():
        try:
            gh("api", f"repos/{repo}/milestones", "-f", f"title=Sprint {s}", "-f", f"description={goal}")
        except RuntimeError:
            print(f"   Sprint {s} already exists, kept")

    print("3/5 Issues")
    numbers, urls = {}, {}
    ordered = sorted(TICKETS, key=lambda t: (t["sprint"], t["key"]))
    for t in ordered:
        labels = [t["epic"], t["priority"]]
        labels.append({"Blocked": "blocked", "Ready for Dev": "ready for dev"}.get(column_of(t), ""))
        url, num = create_issue(f"{t['key']} · {t['title']}", issue_body(t, {}),
                                [label for label in labels if label], f"Sprint {t['sprint']}")
        numbers[t["key"]], urls[t["key"]] = num, url
        print(f"   {t['key']} -> {url}")
    url, num = create_issue("Open questions for Learn@Home", questions_body(numbers), ["client question"])
    numbers["QUESTIONS"], urls["QUESTIONS"] = num, url

    print("4/5 Dependency links")
    for t in ordered:  # second pass: now every issue number is known
        gh("issue", "edit", str(numbers[t["key"]]), "--repo", repo, "--body-file", "-",
           stdin=issue_body(t, numbers))
        for dep in t["blocked_by"]:  # native GitHub "blocked by" relationship (best effort)
            try:
                dep_id = gh("api", f"repos/{repo}/issues/{numbers[dep]}", "--jq", ".id")
                gh("api", "-X", "POST", f"repos/{repo}/issues/{numbers[t['key']]}/dependencies/blocked_by",
                   "-F", f"issue_id={dep_id}")
            except RuntimeError:
                print(f"   (native link {dep} -> {t['key']} not available, the body already lists it)")

    if no_project:
        return
    print("5/5 Project board")
    project = json.loads(gh("project", "create", "--owner", OWNER, "--title", PROJECT_TITLE,
                            "--format", "json") or '{"number": 0, "id": ""}')
    pnum, pid = str(project["number"]), project["id"]
    gh("project", "link", pnum, "--owner", OWNER, "--repo", repo)
    gh("project", "field-create", pnum, "--owner", OWNER, "--name", "Kanban",
       "--data-type", "SINGLE_SELECT", "--single-select-options", ",".join(COLUMNS))
    fields = json.loads(gh("project", "field-list", pnum, "--owner", OWNER, "--format", "json") or '{"fields": []}')
    field = next((f for f in fields["fields"] if f["name"] == "Kanban"), {"id": "", "options": []})
    option = {o["name"]: o["id"] for o in field.get("options", [])}

    for key, url in urls.items():
        item = json.loads(gh("project", "item-add", pnum, "--owner", OWNER, "--url", url,
                             "--format", "json") or '{"id": ""}')
        col = "Backlog" if key == "QUESTIONS" else column_of(BY_KEY[key])
        gh("project", "item-edit", "--id", item["id"], "--project-id", pid,
           "--field-id", field["id"], "--single-select-option-id", option.get(col, ""))

    print("\nDone. Last manual step (30 s): open the project, View 1 -> Layout: Board,"
          " then 'Column by: Kanban'. To share it publicly: Settings -> Visibility -> Public.")


BY_KEY = {t["key"]: t for t in TICKETS}

if __name__ == "__main__":
    try:
        main()
    except RuntimeError as err:
        sys.exit(f"Error: {err}")
