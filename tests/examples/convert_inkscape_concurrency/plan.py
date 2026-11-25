#!/usr/bin/env python3
from stepup.core.api import static
from stepup.report.api import convert_inkscape

for path_svg in static("*.svg"):
    convert_inkscape(path_svg)
