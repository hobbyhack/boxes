---
name: upstream-pr-prep
description: Run before opening a pull request to florianfesti/boxes upstream. Verifies the contribution checklist — new/changed generators are registered, have a ui_group, appear in examples.yml, have a reference SVG, pass pre-commit and pytest, and commit history is clean. Reports a pass/fail summary with concrete fixes. Use when the user says "ready to PR", "prep for upstream", "run the PR checklist", or similar.
disable-model-invocation: true
---

# upstream-pr-prep

Pre-flight checklist for contributing a change to `florianfesti/boxes`. Run every item; report results as a checklist with ✓ / ✗ and, for each ✗, the exact command to fix it.

Refer to the `boxes-contributing` skill for the authoritative contribution rules; this skill *verifies* them.

## Steps

Work in the project root (`$CLAUDE_PROJECT_DIR`). Determine the base branch (usually `master`) and the list of changed files:

```
git fetch origin master
base=$(git merge-base HEAD origin/master)
changed=$(git diff --name-only "$base"...HEAD)
new_gens=$(git diff --name-only --diff-filter=A "$base"...HEAD -- 'boxes/generators/*.py' | grep -v '^boxes/generators/__init__.py$' | grep -v '^boxes/generators/_template.py$')
changed_gens=$(git diff --name-only "$base"...HEAD -- 'boxes/generators/*.py')
```

Run these checks and record pass/fail for each:

1. **Working tree clean** — `git status --porcelain` is empty. If not, the user has uncommitted work; stop and report.

2. **Rebased on current master** — `git merge-base --is-ancestor origin/master HEAD` exits 0. If not, recommend `git rebase origin/master`.

3. **For each new generator file** (`$new_gens`):
   a. **Class name matches filename** — filename `foo_bar.py` may contain any CamelCase class; the class must inherit from `boxes.Boxes` directly or transitively. Grep for `class \w+\(.*Boxes.*\):` in the file.
   b. **`ui_group` attribute set** — `grep -E '^\s*ui_group\s*=' <file>`. Missing or set to `"Unstable"` is allowed but flag `"Unstable"` as a note (won't show in main UI).
   c. **`__init__` calls `Boxes.__init__(self)`** and at least one `addSettingsArgs` — grep for both.
   d. **`render()` method exists** — grep for `def render`.
   e. **Listed in `examples.yml`** — the class name appears as a YAML key, or is under `__ALL__.skipGenerators` / `brokenGenerators` (note if skipped). Use `python -c "import yaml; d=yaml.safe_load(open('examples.yml')); print('<Class>' in d or '<Class>' in d.get('__ALL__',{}).get('skipGenerators',[]) or '<Class>' in d.get('__ALL__',{}).get('brokenGenerators',[]))"`.
   f. **Reference SVG exists** — `tests/data/<Class>.svg` is present and is not 0 bytes.

4. **Pre-commit clean on changed files** —
   `SKIP=pytest pre-commit run --files $changed`. If fails, report the pre-commit output verbatim (trim to 40 lines).

5. **Targeted pytest passes** — for each changed/new generator class, run
   `pytest tests/test_svg.py -k <Class> -q`. Also run the full `pytest tests/` once at the end; mention runtime.

6. **Commit hygiene** — `git log --format='%s' "$base"..HEAD`. Flag: any commit with "WIP", "fixup", "squash!", or merge commits. Upstream prefers a clean linear history.

7. **No accidental files** — `git diff --name-only "$base"...HEAD` does not include: `.claude/**`, `*.svg` outside `examples/` or `tests/data/`, `*.dxf`, `*.plt`, `__pycache__`, `*.egg-info`, `boxes.py.egg-info/`, personal config.

8. **Translation template** — if strings were added (grep changed `.py` files for `_(` additions via `git diff "$base"...HEAD -- '*.py' | grep -E '^\+.*_\('`), remind the user to regenerate `po/boxes.pot` via `scripts/boxes2pot`.

## Output format

One markdown checklist, grouped:

```
## upstream-pr-prep report

### Repo state
- ✓ Working tree clean
- ✓ Rebased on origin/master

### New generators: RoundedTrapezoidBox
- ✓ Class inherits from Boxes
- ✓ ui_group = "Boxes"
- ✗ Not in examples.yml
      fix: add "RoundedTrapezoidBox:" entry, or add to __ALL__.skipGenerators
- ✓ Reference SVG: tests/data/RoundedTrapezoidBox.svg

### Checks
- ✓ pre-commit (0 issues)
- ✓ pytest -k RoundedTrapezoidBox (0.8s)
- ✓ full pytest (42s)
- ✓ commit history clean
- ✓ no stray files

### Ready to PR: NO — fix the ✗ items above.
```

End with a single line: **Ready to PR: YES** or **Ready to PR: NO — N blockers**.

## Guardrails

- Do not modify files. This skill only verifies.
- Do not open the PR; only report readiness.
- Do not commit anything on the user's behalf.
- If the full `pytest` takes longer than 2 minutes, note runtime and continue; don't kill it.
