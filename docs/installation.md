---
description: >-
  Install StepUp Report from PyPI or conda-forge, with pip, uv, pixi or conda,
  on Linux, macOS or Windows,
  which also installs StepUp Core.
---

<!--
SPDX-FileCopyrightText: 2024 Toon Verstraelen <Toon.Verstraelen@UGent.be>
SPDX-License-Identifier: CC-BY-SA-4.0
-->

# Installation

## Requirements

- Linux, macOS or Windows.
  [Supported Platforms][core-platforms] in the documentation of StepUp Core
  explains what differs between them.
  [Windows](#windows) below adds what is specific to StepUp Report.
- [Python](https://www.python.org/) ≥ 3.11.
  On Windows, StepUp Core recommends a minimal patch release for security reasons,
  see its [installation instructions][core-installation].
- A package manager, such as [pip](https://pip.pypa.io/), [uv](https://docs.astral.sh/uv/),
  [pixi](https://pixi.prefix.dev/) or [conda](https://docs.conda.io/).

StepUp Report is published on both [PyPI](https://pypi.org/)
and [conda-forge](https://conda-forge.org/), under the same package name `stepup-report`.
Both also install StepUp Core as a dependency.

We recommend installing into an isolated environment,
such as a [Python virtual environment](https://docs.python.org/3/library/venv.html)
or a pixi workspace,
and activating it with [direnv](https://direnv.net/).

## Installing from PyPI

Use one of the following commands:

```bash
pip install stepup-report     # in an activated virtual environment
uv pip install stepup-report  # same, with uv
uv add stepup-report          # in a uv project
```

## Installing from conda-forge

Use one of the following commands:

```bash
pixi add stepup-report                      # in a pixi workspace
conda install -c conda-forge stepup-report  # in an activated conda environment
```

## WeasyPrint

[`convert_weasyprint()`][stepup.report.api.convert_weasyprint] runs the `weasyprint` command,
which is not installed with StepUp Report.
Install [WeasyPrint](https://weasyprint.org/) in the same environment,
e.g. with one of the following commands:

```bash
pip install weasyprint                  # in an activated virtual environment
uv pip install weasyprint               # same, with uv
pixi add weasyprint                     # in a pixi workspace
conda install -c conda-forge weasyprint # in an activated conda environment
```

WeasyPrint loads the Pango and GLib libraries of GTK, and the HarfBuzz-Subset library.
Pip and uv do not install these libraries,
but conda-forge installs Pango and GLib together with WeasyPrint.
As of WeasyPrint 70.0, a missing HarfBuzz-Subset library only causes a `DeprecationWarning`,
but future versions of WeasyPrint will require it.
On Debian and Ubuntu, it is provided by the package `libharfbuzz-subset0`.
Install them as explained in the [documentation of WeasyPrint][weasyprint-first-steps].

## Windows

StepUp Report runs natively on Windows, without WSL.
The [Windows section of Supported Platforms][core-windows]
explains what a workflow has to take care of on Windows,
e.g. how to put a path into a command.
The rest of this section is specific to StepUp Report.

### Tested Functions

The test suite runs on Windows for the following functions of `stepup.report.api`,
with Tectonic 0.17 and Typst 0.15 as the only external programs:

- [`add_notes_pdf()`][stepup.report.api.add_notes_pdf]
- [`cat_pdf()`][stepup.report.api.cat_pdf]
- [`check_hrefs()`][stepup.report.api.check_hrefs]
- [`compile_tectonic()`][stepup.report.api.compile_tectonic]
- [`compile_typst()`][stepup.report.api.compile_typst]
- [`convert_markdown()`][stepup.report.api.convert_markdown]
- [`flatten_latex()`][stepup.report.api.flatten_latex]
- [`nup_pdf()`][stepup.report.api.nup_pdf]
- [`raster_pdf()`][stepup.report.api.raster_pdf]
- [`sanitize_bibtex()`][stepup.report.api.sanitize_bibtex]
- [`unplot()`][stepup.report.api.unplot]

### Untested Functions

The following functions are not tested on Windows,
because the programs or libraries they need are not installed for the tests:

- [`compile_latex()`][stepup.report.api.compile_latex]
  needs a LaTeX distribution, such as TeX Live.
- [`convert_inkscape()`][stepup.report.api.convert_inkscape]
  needs Inkscape.
- [`convert_weasyprint()`][stepup.report.api.convert_weasyprint]
  needs [WeasyPrint and its libraries](#weasyprint).
- [`diff_latex()`][stepup.report.api.diff_latex]
  needs `latexdiff` and a [POSIX shell](#posix-shell).

### POSIX Shell

[`diff_latex()`][stepup.report.api.diff_latex] creates steps that run in a shell.
On Windows, such steps need a POSIX shell, e.g. the one of Git for Windows,
see [POSIX Shell on Windows][core-posix-shell].
The other functions do not need a shell.

### Tectonic

As observed with Tectonic 0.17,
Tectonic on Windows prints `Fontconfig error: Cannot load default config file` on every run,
unless the environment variable `FONTCONFIG_FILE` names a fontconfig configuration.
The steps of [`compile_tectonic()`][stepup.report.api.compile_tectonic] still succeed.
[Tests on Windows](development.md#tests-on-windows) shows how to set this variable.

### Text Files

All tools of StepUp Report read text files as UTF-8,
and write them as UTF-8 with `\n` line endings, on every platform.
Save your sources, e.g. LaTeX, Markdown and BibTeX files, as UTF-8.

[core-platforms]: https://reproducible-reporting.github.io/stepup-core/platforms/
[core-windows]: https://reproducible-reporting.github.io/stepup-core/platforms/#windows
[core-installation]: https://reproducible-reporting.github.io/stepup-core/installation/
[core-posix-shell]: https://reproducible-reporting.github.io/stepup-core/installation/#posix-shell-on-windows
[weasyprint-first-steps]: https://doc.courtbouillon.org/weasyprint/stable/first_steps.html
