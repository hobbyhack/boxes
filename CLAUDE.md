# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Boxes.py is a parametric generator for laser-cut boxes. It outputs SVG (and via `pstoedit`: DXF, gcode, PLT). It is simultaneously a Python library, a CLI, a web server, and an Inkscape plug-in. GPLv3+, Python 3.10+.

## Common commands

Install for development:

```
pip install .[dev]      # runtime + lxml, mypy, pytest, pre-commit
pip install .[doc]      # sphinx for docs
```

Scripts run straight from the git checkout (no install needed):

- `scripts/boxes <GeneratorName> [--param=value ...] [-o out.svg]` — CLI render
- `scripts/boxesserver` — web UI on port 8000 (`docker compose up` exposes it on 4455)
- `scripts/boxes2inkscape` — generate Inkscape extension `.inx` files
- `scripts/boxes2pot` — extract gettext strings

Tests (pytest):

```
pytest tests/                                  # all
pytest tests/test_svg.py::TestSVG -k HeartBox  # one generator
```

The test suite renders every generator listed in `examples.yml` (except entries under `__ALL__.skipGenerators` / `brokenGenerators`) and diffs the SVG output against `tests/data/`. When adding a generator, update `examples.yml` accordingly.

Lint / style: `pre-commit run --all-files` (install with `pre-commit install`). Type check: `mypy` (config in `pyproject.toml`).

Build docs: `cd documentation/src && make html`.

## Architecture

Tiers (see `documentation/src/api_architecture.rst` for the full version):

1. **User interfaces** in `boxes/scripts/` (`boxes_main.py` CLI, `boxesserver.py` web, `boxes_proxy.py` Inkscape bridge). They discover generators by class name.
2. **Generators** in `boxes/generators/*.py` — each is a subclass of `boxes.Boxes`. Registered automatically by filename/class-name; see `boxes/generators/__init__.py` (`getAllBoxGenerators`) and the `ui_group` class attribute for grouping in the UI. Copy `_template.py` as a starting point and rename the class.
3. **Parts** — methods on `Boxes` that draw one shape. Must accept a `move=` parameter. Most accept per-edge callbacks for inner features (holes, slots); use callbacks rather than absolute coordinates so inner features stay aligned regardless of edge type.
4. **Edges** (`boxes/edges.py`, `boxes/walledges.py`, `boxes/lids.py`) — turtle-graphics commands promoted to classes so they can advertise outsets and be parameterised via `*Settings` classes. Each standard edge has a single-char key (e.g. `e`, `f`, `F`, `h`) so part edge-lists can be passed as strings like `"FFeF"`.
5. **Turtle graphics + back end** — All drawing is relative: `self.moveTo`, `self.edge`, `self.corner`, etc. Back end is the pure-Python `boxes/drawing.py` (`Boxes.ctx`); cairo is no longer used.

Sign conventions matter for kerf ("burn") correction:

- Positive corner angles (counter-clockwise) close a part; negative (clockwise) create protrusions.
- **Holes are drawn clockwise** — inverted from outlines. Getting the winding right is what makes `--burn` produce correct press-fit gaps.

Generator authoring essentials:

- `__init__` calls `Boxes.__init__(self)`, then `self.addSettingsArgs(...)` for each edge family it uses, then `self.buildArgParser(...)` / `self.argparser.add_argument(...)` for user parameters. Common shared params (`x`, `y`, `h`, `sx`, `sy`, `thickness`, `burn`, `tabs`, ...) come pre-wired via `buildArgParser`.
- `render()` does the drawing. Pull locals (`x, y, h = self.x, self.y, self.h; t = self.thickness`) for readable code.
- `ui_group` controls the web UI category; `"Unstable"` hides work-in-progress generators from the main groupings.

Other notable modules: `boxes/formats.py` (SVG → DXF/PLT/gcode via `pstoedit`, hard-coded at `/usr/bin/pstoedit`), `boxes/gears.py`, `boxes/pulley.py`, `boxes/servos.py`, `boxes/qrcode_factory.py` (reusable part-level helpers), `boxes/extents.py` (layout/bounding-box math), `boxes/svgmerge.py` (combines multi-part SVGs).

Translations: `po/` (gettext catalogues), `locale/` (compiled `.mo`). `boxes2pot` regenerates the template.
