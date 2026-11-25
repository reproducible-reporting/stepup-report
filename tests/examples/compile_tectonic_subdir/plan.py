#!/usr/bin/env python3

from stepup.core.api import run, static
from stepup.report.api import compile_tectonic

static("sub/paper.tex", "sub/smile.pdf", "sub/references.bib")
compile_tectonic("sub/paper.tex", keep_deps=True, step_info="current_step_info.json")
run("echo 'Hi there!' > generated.tex", out=["generated.tex"], workdir="sub", shell=True)
