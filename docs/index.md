---
title: A Build Tool for Scientific Writing
description: >-
  StepUp Report is a StepUp extension that builds scientific documents
  from LaTeX, Typst and Markdown sources, figures, PDF files and BibTeX databases.
---

<!--
SPDX-FileCopyrightText: 2024 Toon Verstraelen <Toon.Verstraelen@UGent.be>
SPDX-License-Identifier: CC-BY-SA-4.0
-->

<!-- The front matter sets the HTML title of the page, not a second heading. -->
<!-- pyml disable-num-lines 3 single-title -->

# StepUp Report: A Build Tool for Scientific Writing

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

!!! warning "StepUp Report is in early development, and its API may still change."

    For now, it only contains the PDF tools, the LaTeX, Tectonic and Typst steps,
    the BibTeX cleanup, the conversions with Inkscape, Markdown and WeasyPrint,
    the hyperlink check and Unplot of StepUp RepRep 4.2,
    see the [API reference](reference/stepup.report.api.md).
    For production use, keep using
    [StepUp RepRep 4.2](https://reproducible-reporting.github.io/stepup-reprep/),
    which contains all of the features above.
