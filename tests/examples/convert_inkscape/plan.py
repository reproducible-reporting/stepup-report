#!/usr/bin/env python3
from stepup.core.api import static
from stepup.report.api import convert_inkscape

static("smile.svg", "glasses.svg")
convert_inkscape("glasses.svg", "glasses.png", optional=True)
convert_inkscape("smile.svg", "final.pdf", step_info="current_step_info.json")
