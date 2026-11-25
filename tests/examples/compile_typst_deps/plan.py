#!/usr/bin/env python3
from stepup.core.api import run, static
from stepup.report.api import compile_typst

static("image.py", "document.typ")
compile_typst("document.typ")
run("./image.py", out="image.jpg")
