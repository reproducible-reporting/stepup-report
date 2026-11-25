---
description: >-
  Archive the sources and outputs of a compiled LaTeX, Tectonic or Typst document,
  e.g. to send them to a journal,
  with a step info file and the inventory tools of StepUp Data.
---

<!--
SPDX-FileCopyrightText: 2026 Toon Verstraelen <Toon.Verstraelen@UGent.be>
SPDX-License-Identifier: CC-BY-SA-4.0
-->

# Archiving the Files of a Compiled Document

A journal often asks for the sources of a manuscript,
e.g. the LaTeX files, the figures and the `.bbl` file.
Collecting them by hand is error-prone,
because the compile step knows best which files the document needs.
StepUp Report writes that knowledge to a step info file,
which another tool can read to select the files to archive.

## Writing a Step Info File

[`compile_latex()`][stepup.report.api.compile_latex],
[`compile_tectonic()`][stepup.report.api.compile_tectonic]
and [`compile_typst()`][stepup.report.api.compile_typst]
take a keyword argument `step_info`,
the path of a JSON file to which the step writes its sources and outputs when it succeeds.
The file has the format of [Step Info Files][core-step-info-files] in StepUp Core.
For example, the following `plan.py` compiles a paper with a bibliography:

```python
from stepup.core.api import static
from stepup.report.api import compile_latex

static("paper.tex", "references.bib")
compile_latex("paper.tex", step_info="paper-info.json")
```

When `paper.tex` includes no other files, the step info file lists:

- under `inp`: `paper.tex` and `references.bib`,
- under `out`: `paper.aux`, `paper.bbl` and `paper.pdf`.

The documentation of each function explains which files it lists.
For `compile_latex()`, these also include the local files that only LaTeX knows about,
such as the class and style files of a journal template in your project.
Volatile files are never listed,
and neither are the files of the TeX distribution, unless `${STEPUP_PATH_FILTER}` retains them.
The step info file is an output of the compile step, but it does not list itself.

The figures of a document may have dependencies of their own.
[`convert_inkscape()`][stepup.report.api.convert_inkscape]
and [`convert_weasyprint()`][stepup.report.api.convert_weasyprint]
also take a keyword argument `step_info`,
which lists the images and style sheets used by an SVG or HTML file.

## Making a ZIP File with StepUp Data

[StepUp Data][stepup-data] is an optional companion of StepUp Report,
which makes inventories of files and packs them into ZIP files.
StepUp Report does not depend on it, so install it separately when you need it.
Its function `make_inventory()` reads the `inp` or `out` paths of step info files,
and `zip_inventory()` packs the files of an inventory:

```python
from stepup.core.api import static
from stepup.data.api import make_inventory, zip_inventory
from stepup.report.api import compile_latex

static("paper.tex", "references.bib")
compile_latex("paper.tex", step_info="paper-info.json")
make_inventory(
    "paper-sources.jsonl",
    include_info_inp="paper-info.json",
    include_info_out="paper-info.json",
    exclude="*.aux",
)
zip_inventory("paper-sources.jsonl", "paper-sources.zip")
```

The argument `include_info_inp` adds the sources of the document,
and `include_info_out` adds its outputs, here the `.bbl` file and the PDF.
The argument `exclude` leaves out files that the journal does not need.
Pass the step info file only to `include_info_inp` to archive just the sources.
When the `.bbl` file is a source, i.e. with `run_bibtex=False`,
it is listed under `inp` instead.

The inventory is made after the compile step,
because the step info file is one of its inputs.
See [Inventory Files][data-inventory-files] in the documentation of StepUp Data
for all options of `make_inventory()` and `zip_inventory()`.

[core-step-info-files]: https://reproducible-reporting.github.io/stepup-core/tutorials/step_info/#step-info-files
[stepup-data]: https://reproducible-reporting.github.io/stepup-data/
[data-inventory-files]: https://reproducible-reporting.github.io/stepup-data/tutorials/inventory_files/
