#!/usr/bin/env python3

from stepup.core.api import run, static
from stepup.report.api import compile_latex

static("paper.tex", "smile.pdf", "smiley.sty")
compile_latex("paper.tex", step_info="current_step_info.json")
run("echo 'Hi there!' > generated.tex", out=["generated.tex"], shell=True)
