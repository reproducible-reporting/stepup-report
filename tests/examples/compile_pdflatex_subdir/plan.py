#!/usr/bin/env python3

from stepup.core.api import run, static
from stepup.report.api import compile_latex

static("sub/paper.tex", "sub/smile.pdf", "sub/references.bib")
compile_latex("sub/paper.tex", step_info="current_step_info.json")
run("echo 'Hi there!' > generated.tex", out=["generated.tex"], workdir="sub", shell=True)
