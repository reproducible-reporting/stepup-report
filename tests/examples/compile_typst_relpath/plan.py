#!/usr/bin/env python3
from stepup.core.api import static
from stepup.report.api import compile_typst

static(
    "source/document.typ",
    "source/tada.svg",
    "source/data/productivity.csv",
)
compile_typst("source/document.typ", "out.pdf", step_info="current_step_info.json", keep_deps=True)
