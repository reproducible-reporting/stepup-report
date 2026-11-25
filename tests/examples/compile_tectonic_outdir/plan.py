#!/usr/bin/env python3

from stepup.core.api import static
from stepup.report.api import compile_tectonic

static("sub/paper.tex")
compile_tectonic("sub/paper.tex", "out/", step_info="current_step_info.json")
