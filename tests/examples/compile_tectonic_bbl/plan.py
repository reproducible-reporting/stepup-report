#!/usr/bin/env python3

from stepup.core.api import static
from stepup.report.api import compile_tectonic

static("paper.tex", "paper.bbl")
compile_tectonic("paper.tex", step_info="current_step_info.json")
