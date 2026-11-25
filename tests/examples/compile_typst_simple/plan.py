#!/usr/bin/env python3
from stepup.core.api import static
from stepup.report.api import compile_typst

static("document.typ")
compile_typst("document.typ", "out.pdf", step_info="current_step_info.json")
