#!/usr/bin/env python3

from stepup.core.api import static
from stepup.report.api import compile_latex

static("paper.tex")
compile_latex("paper.tex", step_info="current_step_info.json")
