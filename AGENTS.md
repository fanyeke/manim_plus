# AGENTS.md

## Cursor Cloud specific instructions

### Project Overview

`manim_plus` (manim+) is a Python project extending [Manim Community](https://www.manim.community/) — a mathematical animation engine. The project is in early stages.

### Tech Stack

- **Python 3.12+** with virtual environment at `.venv/`
- **Manim Community v0.20.1** — core animation library
- **FFmpeg** — video encoding (system dependency, pre-installed)
- **LaTeX (TeX Live)** — math typesetting (system dependency, needs `apt install`)
- **Cairo + Pango** — 2D graphics rendering (system dependencies)

### System Dependencies (already installed in snapshot)

These system packages are required and installed via apt:
- `texlive texlive-latex-extra texlive-fonts-extra texlive-latex-recommended texlive-science texlive-fonts-recommended`
- `libcairo2-dev libpango1.0-dev pkg-config python3-dev python3-venv`
- `ffmpeg` (pre-installed in base image)

### Running the Application

Activate the virtual environment first:
```bash
source .venv/bin/activate
```

Render a Manim scene:
```bash
manim render -ql scene_file.py SceneName    # low quality (480p, fast preview)
manim render -qm scene_file.py SceneName    # medium quality (720p)
manim render -qh scene_file.py SceneName    # high quality (1080p)
```

Output videos are written to `media/videos/`.

### Linting & Testing

```bash
ruff check .                # lint (note: F403/F405 for `from manim import *` is expected Manim idiom)
python -m pytest            # run tests
```

### Key Gotchas

- Manim's standard import pattern is `from manim import *`. This triggers ruff F403/F405 warnings which are expected and should be suppressed in ruff config for Manim scene files.
- LaTeX rendering requires TeX Live system packages. If LaTeX-based scenes fail with `dvisvgm` errors, ensure texlive packages are installed.
- Rendered media files go to `media/` directory — this should be in `.gitignore`.
