#!/usr/bin/env python3

from stepup.core.api import static
from stepup.report.api import compile_latex

static("paper.tex", "paper.bbl")
compile_latex("paper.tex", run_bibtex=False, step_info="current_step_info.json")
