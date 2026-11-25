#!/usr/bin/env python3
from stepup.core.api import static
from stepup.report.api import flatten_latex

static("sub/article_structured.tex", "sub/part1.tex", "sub/part2.tex")
flatten_latex("sub/article_structured.tex", "sub/article.tex")
