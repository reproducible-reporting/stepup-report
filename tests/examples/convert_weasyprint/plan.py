#!/usr/bin/env python3
from stepup.core.api import static
from stepup.report.api import convert_weasyprint

static("doc.html", "block.png", "style.css")
convert_weasyprint("doc.html", step_info="current_step_info.json")
