#!/usr/bin/env python3

from stepup.core.api import run, static
from stepup.report.api import compile_latex

static("paper.tex")
compile_latex("paper.tex", step_info="current_step_info.json")
run(
    "echo 'Verbatim input:\\verbatiminput{code.txt}' > subdir/generated.tex",
    out=["subdir/generated.tex"],
    shell=True,
)
run("echo '2 + 2' > subdir/code.txt", out=["subdir/code.txt"], shell=True)
