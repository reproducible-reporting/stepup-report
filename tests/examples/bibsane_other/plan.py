#!/usr/bin/env python3
from stepup.core.api import copy, static
from stepup.report.api import sanitize_bibtex

static("references.bib", "paper.aux", "bibsane.yaml")
sanitize_bibtex("references.bib", "cleaned.bib", path_aux="paper.aux", path_config="bibsane.yaml")
copy("cleaned.bib", "copy.bib")
