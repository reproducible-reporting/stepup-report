#!/usr/bin/env python3
from stepup.core.api import static
from stepup.report.api import sanitize_bibtex

static("references.bib", "paper.aux", "bibsane.yaml")
sanitize_bibtex("references.bib", path_aux="paper.aux", path_config="bibsane.yaml")
