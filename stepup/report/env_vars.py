# SPDX-FileCopyrightText: 2026 Toon Verstraelen <Toon.Verstraelen@UGent.be>
# SPDX-License-Identifier: LGPL-3.0-or-later
"""The `STEPUP_REPORT_*` environment variables of StepUp Report.

They are registered with StepUp Core through the `stepup.env_vars` entry point,
so that `stepup config` lists them and checks the values of those that are parsed.
"""

import shlex

from stepup.core.converters import boolean, positive_int
from stepup.core.env_vars import EnvVarInfo, EnvVarRegistry

__all__ = ("env_vars",)


# Programs, configuration files and other values that are used as they are.
_PLAIN = (
    "STEPUP_REPORT_BIBTEX",
    "STEPUP_REPORT_CHECK_HREFS_CONFIG",
    "STEPUP_REPORT_INKSCAPE",
    "STEPUP_REPORT_LATEX",
    "STEPUP_REPORT_LATEXDIFF",
    "STEPUP_REPORT_MARKDOWN_CSS",
    "STEPUP_REPORT_NUP_PAGE_FORMAT",
    "STEPUP_REPORT_TECTONIC",
    "STEPUP_REPORT_TYPST",
    "STEPUP_REPORT_WEASYPRINT",
)

# Extra command-line arguments, split like a POSIX shell would.
_ARGS = (
    "STEPUP_REPORT_INKSCAPE_PDF_ARGS",
    "STEPUP_REPORT_INKSCAPE_PNG_ARGS",
    "STEPUP_REPORT_LATEXDIFF_ARGS",
    "STEPUP_REPORT_TECTONIC_ARGS",
    "STEPUP_REPORT_TYPST_ARGS",
)

_BOOLEAN = (
    "STEPUP_REPORT_TECTONIC_KEEP_DEPS",
    "STEPUP_REPORT_TYPST_KEEP_DEPS",
)

_POSITIVE_INT = (
    "STEPUP_REPORT_NUP_NCOL",
    "STEPUP_REPORT_NUP_NROW",
    "STEPUP_REPORT_RASTER_QUALITY",
    "STEPUP_REPORT_RASTER_RESOLUTION",
    "STEPUP_REPORT_TYPST_RESOLUTION",
)


def env_vars() -> EnvVarRegistry:
    """Return the environment variables of StepUp Report."""
    infos = {name: EnvVarInfo(secret=False) for name in _PLAIN}
    infos.update({name: EnvVarInfo(secret=False, validator=shlex.split) for name in _ARGS})
    infos.update({name: EnvVarInfo(secret=False, validator=boolean) for name in _BOOLEAN})
    infos.update({name: EnvVarInfo(secret=False, validator=positive_int) for name in _POSITIVE_INT})
    # A margin of zero is valid, so the value is only checked as the code parses it.
    infos["STEPUP_REPORT_NUP_MARGIN"] = EnvVarInfo(secret=False, validator=float)
    return EnvVarRegistry("StepUp Report", infos)
