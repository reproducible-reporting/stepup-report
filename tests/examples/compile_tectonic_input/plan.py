#!/usr/bin/env python3

from stepup.core.api import run, static
from stepup.report.api import compile_tectonic

static("paper.tex", "smile.pdf")
compile_tectonic("paper.tex", keep_deps=True, step_info="current_step_info.json")
run("echo 'Hi there!' > generated.tex", out=["generated.tex"], shell=True)
