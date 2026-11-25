<!--
SPDX-FileCopyrightText: 2024 Toon Verstraelen <Toon.Verstraelen@UGent.be>
SPDX-License-Identifier: LGPL-3.0-or-later
-->

# StepUp Report

[![release](https://github.com/reproducible-reporting/stepup-report/actions/workflows/release.yaml/badge.svg?branch=main)](https://github.com/reproducible-reporting/stepup-report/actions/workflows/release.yaml)
[![pytest](https://github.com/reproducible-reporting/stepup-report/actions/workflows/pytest.yaml/badge.svg?branch=main)](https://github.com/reproducible-reporting/stepup-report/actions/workflows/pytest.yaml)
[![docs](https://github.com/reproducible-reporting/stepup-report/actions/workflows/docs.yaml/badge.svg?branch=main)](https://github.com/reproducible-reporting/stepup-report/actions/workflows/docs.yaml)
[![PyPI Version](https://img.shields.io/pypi/v/stepup-report)](https://pypi.org/project/stepup-report/)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/stepup-report)
![LGPL-3 License](https://img.shields.io/badge/License-LGPL_v3-blue.svg)
[![CodeFactor](https://www.codefactor.io/repository/github/reproducible-reporting/stepup-report/badge)](https://www.codefactor.io/repository/github/reproducible-reporting/stepup-report)

<!-- snipwise.md BEGIN abstract -->
StepUp Report is an extension of the
[StepUp Core](https://reproducible-reporting.github.io/stepup-core/) build tool
for writing reproducible reports.
It compiles LaTeX, Typst and Markdown sources,
converts figures with Inkscape,
post-processes PDF files,
and cleans up BibTeX databases.
StepUp Core tracks the inputs and outputs of each step,
so only the steps affected by a change are rerun.
StepUp Report is part of
[Reproducible Reporting](https://github.com/reproducible-reporting).
<!-- snipwise.md END abstract -->

> **Note:** StepUp Report is in early development, and its API may still change.
> For now, it only contains the PDF tools, the LaTeX, Tectonic and Typst steps,
> the BibTeX cleanup, the conversions with Inkscape, Markdown and WeasyPrint,
> the hyperlink check and Unplot of StepUp RepRep 4.2.
> For production use, keep using
> [StepUp RepRep 4.2](https://reproducible-reporting.github.io/stepup-reprep/),
> which contains all of the features above.

For more information, consult the [documentation](https://reproducible-reporting.github.io/stepup-report/).
The source code is hosted on [GitHub](https://github.com/reproducible-reporting/stepup-report).
