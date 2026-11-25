#!/usr/bin/env python3
from stepup.core.api import static
from stepup.report.api import convert_markdown

static("sub/demo.md", "sub/demo.css", "page.css")
convert_markdown("sub/demo.md", paths_css="page.css")
