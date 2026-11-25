#!/usr/bin/env python3
from stepup.core.api import static
from stepup.report.api import compile_typst

static("sub/document.typ")
compile_typst("${ROOT}/sub/document.typ", "${ROOT}/sub/out.pdf", workdir="sub")
