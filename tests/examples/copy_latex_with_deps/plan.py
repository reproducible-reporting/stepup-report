#!/usr/bin/env python3
from stepup.core.api import copy, static
from stepup.report.latex_deps import scan_latex_deps

static("doc.tex", "snippet.tex", "first.dat", "second.dat")
inp, bib, out, vol = scan_latex_deps("doc.tex")
for path in inp:
    copy(path, "dest/")
