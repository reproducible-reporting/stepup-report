#!/usr/bin/env python3
from stepup.core.api import static
from stepup.report.api import compile_typst

static("error.typ")
compile_typst("error.typ", keep_deps=True)
