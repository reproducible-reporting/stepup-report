#!/usr/bin/env python3

from stepup.core.api import static
from stepup.report.api import check_hrefs, compile_latex

static("README.txt", "main.tex", "check_hrefs.yaml")
compile_latex("main.tex", step_info="current_step_info.json")
check_hrefs("main.pdf")
