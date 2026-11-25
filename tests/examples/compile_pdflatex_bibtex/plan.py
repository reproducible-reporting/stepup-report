#!/usr/bin/env python3

from stepup.core.api import static
from stepup.report.api import compile_latex, sanitize_bibtex

static("paper.tex", "bibsane.yaml", "references.bib")
compile_latex("${LATEX_MAIN}.tex", step_info="current_step_info.json")
sanitize_bibtex("references.bib", path_aux="${LATEX_MAIN}.aux", path_config="bibsane.yaml")
