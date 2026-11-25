#!/usr/bin/env python3

from stepup.core.api import static
from stepup.report.api import compile_tectonic, sanitize_bibtex

static("paper.tex", "bibsane.yaml", "references.bib")
compile_tectonic("${LATEX_MAIN}.tex", step_info="current_step_info.json")
sanitize_bibtex("references.bib", path_config="bibsane.yaml")
