#!/usr/bin/env python3
from stepup.core.api import static
from stepup.report.api import unplot

static("plot.svg")
unplot("plot.svg")
