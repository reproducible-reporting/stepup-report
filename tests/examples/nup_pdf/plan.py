#!/usr/bin/env python3
from stepup.core.api import static
from stepup.report.api import nup_pdf

static("src.pdf")
nup_pdf("src.pdf", "dst.pdf", page_format="A4")
