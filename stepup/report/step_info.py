# SPDX-FileCopyrightText: 2024 Toon Verstraelen <Toon.Verstraelen@UGent.be>
# SPDX-License-Identifier: LGPL-3.0-or-later
"""Step info files with the dependencies of a step."""

from collections.abc import Collection

from stepup.core.api import get_amended_info, get_info
from stepup.core.path import Path, StrPath
from stepup.core.stepinfo import dump_step_info

__all__ = ("write_step_info",)


def write_step_info(path_step_info: StrPath, exclude: Collection[StrPath] = ()):
    """Write the dependencies of the current step to a step info file.

    The step info has the command and working directory of the current step.
    It lists the dependencies declared when the step was defined,
    and those amended so far by the current process,
    except for the step info file itself and the paths in `exclude`.
    Volatile outputs are never listed.

    Parameters
    ----------
    path_step_info
        The step info file, in the format of `dump_step_info()` of StepUp Core.
    exclude
        Paths of dependencies to leave out,
        e.g. files that only serve the bookkeeping of the step.

    Notes
    -----
    The current directory must be the working directory of the step,
    because `path_step_info` and `exclude` are compared to the paths of `get_info()`,
    which are relative to that directory.
    """
    info = get_info().merge(get_amended_info())
    excluded = {Path(path).normpath() for path in [path_step_info, *exclude]}
    info.inp = [path for path in info.inp if path not in excluded]
    info.out = [path for path in info.out if path not in excluded]
    info.vol = []
    dump_step_info(path_step_info, info)
