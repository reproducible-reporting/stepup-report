---
description: >-
  Release notes for every version of StepUp Report,
  following Keep a Changelog and effort-based versioning.
---

<!--
SPDX-FileCopyrightText: 2024 Toon Verstraelen <Toon.Verstraelen@UGent.be>
SPDX-License-Identifier: CC-BY-SA-4.0
-->

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Effort-based Versioning](https://jacobtomlinson.dev/effver/).
(Changes to features documented as "experimental" will not increment macro and meso version numbers.)

## [Unreleased][]

(no changes yet)

## [4.3.0a0][] - 2026-11-25 {: #v4.3.0a0 }

### Added

The following features of StepUp RepRep 4.2 moved to StepUp Report.
Apart from the changes listed below, their behavior is unchanged,
only their names and some arguments differ:

- The PDF tools [`add_notes_pdf()`][stepup.report.api.add_notes_pdf],
  [`cat_pdf()`][stepup.report.api.cat_pdf],
  [`nup_pdf()`][stepup.report.api.nup_pdf]
  and [`raster_pdf()`][stepup.report.api.raster_pdf].
- The compile steps [`compile_latex()`][stepup.report.api.compile_latex],
  [`compile_tectonic()`][stepup.report.api.compile_tectonic]
  and [`compile_typst()`][stepup.report.api.compile_typst],
  and the LaTeX tools [`flatten_latex()`][stepup.report.api.flatten_latex]
  and [`diff_latex()`][stepup.report.api.diff_latex].
- The BibTeX cleanup [`sanitize_bibtex()`][stepup.report.api.sanitize_bibtex].
- The conversions [`convert_inkscape()`][stepup.report.api.convert_inkscape],
  [`convert_markdown()`][stepup.report.api.convert_markdown]
  and [`convert_weasyprint()`][stepup.report.api.convert_weasyprint].
- The hyperlink check [`check_hrefs()`][stepup.report.api.check_hrefs]
  and [`unplot()`][stepup.report.api.unplot].

They are renamed as follows:

- The functions are imported from `stepup.report.api` instead of `stepup.reprep.api`.
- The commands start with `sr-` instead of `srr-`, e.g. `sr-compile-latex`.
- The environment variables start with `STEPUP_REPORT_` instead of `REPREP_`,
  e.g. `STEPUP_REPORT_LATEX` and `STEPUP_REPORT_NUP_NROW`.
- The `%REPREP inp`, `out`, `vol` and `ignore` markers in LaTeX sources keep their names.

The `STEPUP_REPORT_*` variables are registered with StepUp Core,
so `stepup config` lists them and reports values that cannot be parsed.

New features compared to StepUp RepRep 4.2:

- `raster_pdf()` renders the pages of a PDF into PNG files when `dest` ends with `.png`.
  The page placeholders `{p}`, `{0p}` and `{t}` in the name of the output
  have the same meaning as in `compile_typst()`.
  This replaces `convert_mutool_png()` of 4.2.
- `convert_inkscape()` and `convert_weasyprint()` take a keyword argument `step_info`,
  like the compile steps.
  The step info file lists the images and style sheets used by the SVG or HTML file.

### Changed

Compared to StepUp RepRep 4.2:

- The argument `step_info=` of `compile_latex()`, `compile_tectonic()` and `compile_typst()`
  replaces `inventory=`, and the option `--step-info` of their commands replaces `--inventory`.
  The step writes its dependencies to a step info file in the format of StepUp Core,
  instead of an inventory file of its own,
  and only when the step succeeds.
  The step info file lists the files of the inventory of 4.2, divided over inputs and outputs.
  The step info of `compile_latex()` also lists the files that LaTeX reports in the `.fls` file,
  such as local class and style files, but not the `.fls` file itself.
  [Archiving the Files of a Compiled Document](tutorials/archive_sources.md)
  explains how to make an inventory or a ZIP file from it with StepUp Data.
- All functions take the input paths and the output destination `dest` as positional arguments,
  and all other arguments as keyword-only arguments.
  The following arguments changed:
    - `add_notes_pdf(path_pdf, path_notes, dest)`,
      `nup_pdf(path_pdf, dest)` and `raster_pdf(path_pdf, dest)`:
      the input is `path_pdf`, and `dest` may also be a directory.
    - `cat_pdf(paths_pdf, dest)`: the inputs are `paths_pdf`.
    - `check_hrefs(path_src, *, path_config)`:
      `path_config`, `resources` and `duration` are keyword-only.
    - `diff_latex(path_old, path_new, dest)`: `dest` may also be a directory.
    - `flatten_latex(path_tex, dest=None)`: the default output is `{stem}-flat.tex`.
    - `sanitize_bibtex(path_bib, dest=None, *, path_aux, path_config)`:
      `dest` replaces `path_out`, `path_config` replaces `path_cfg`,
      and `overwrite` is removed, because `dest=None` already overwrites the BibTeX file.
- `convert_inkscape(path_svg, dest=None)` replaces `convert_inkscape(path_svg, path_out)`,
  `convert_inkscape_pdf()` and `convert_inkscape_png()`.
  The output is a PDF by default, and a PNG when `dest` ends with `.png`.
- WeasyPrint is no longer installed with StepUp Report.
  Install it yourself to use `convert_weasyprint()`,
  as explained in the [installation instructions](installation.md#weasyprint).

### Removed

Compared to StepUp RepRep 4.2:

- The variables `REPREP_LATEX_INVENTORY`, `REPREP_TECTONIC_INVENTORY`
  and `REPREP_TYPST_INVENTORY` have no successor.
  Pass `step_info=` to each compile step that needs one.
- `convert_inkscape_pdf()` and `convert_inkscape_png()`,
  which `convert_inkscape()` replaces.

### Fixed

Compared to StepUp RepRep 4.2:

- `diff_latex()` reads `STEPUP_REPORT_LATEXDIFF_ARGS` when `latexdiff_args` is not given.
  In 4.2, `REPREP_LATEXDIFF_ARGS` only had an effect with `latexdiff_args=None`.
- The help of `sr-convert-inkscape` names `STEPUP_REPORT_INKSCAPE_PNG_ARGS`
  for PNG output, instead of the variable for PDF output.
- `convert_markdown()` accepts a `pathlib.Path` as `paths_css`, which raised a `TypeError` in 4.2,
  and more than one CSS file, which made `sr-convert-markdown` fail in 4.2.

[Unreleased]: https://github.com/reproducible-reporting/stepup-report
[4.3.0a0]: https://github.com/reproducible-reporting/stepup-report/releases/tag/v4.3.0a0
