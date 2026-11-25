#!/usr/bin/env python3
from stepup.core.api import static
from stepup.report.api import compile_typst

static("lorem.typ")
compile_typst("lorem.typ", "out-{0p}-{t}.png", keep_deps=True)
