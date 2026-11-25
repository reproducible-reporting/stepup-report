#!/usr/bin/env python3
from stepup.core.api import static
from stepup.report.api import convert_markdown

static("source/demo.md", "common/")
convert_markdown("source/demo.md")
