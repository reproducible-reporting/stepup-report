# SPDX-FileCopyrightText: 2026 Toon Verstraelen <Toon.Verstraelen@UGent.be>
# SPDX-License-Identifier: LGPL-3.0-or-later
"""Tests for stepup.report.env_vars."""

import ast
import os
import re
import subprocess
import sys

import stepup.report
from stepup.core.cli.env_vars_loader import core_env_vars
from stepup.core.path import Path
from stepup.report.env_vars import env_vars

# `convert_inkscape` builds these names from the extension of the output file.
INKSCAPE_ARGS = {"STEPUP_REPORT_INKSCAPE_PDF_ARGS", "STEPUP_REPORT_INKSCAPE_PNG_ARGS"}


def _string_constants(source: str) -> set[str]:
    """Return every string literal in a module that has the form of a StepUp variable name.

    A literal with a trailing underscore is the start of an f-string, not a name.
    """
    return {
        node.value
        for node in ast.walk(ast.parse(source))
        if isinstance(node, ast.Constant)
        and isinstance(node.value, str)
        and re.fullmatch("STEPUP_[A-Z0-9_]*[A-Z0-9]", node.value)
    }


def test_env_vars_are_registered():
    """Every variable that StepUp Report reads is registered, and vice versa.

    A variable that is read but not registered would be listed by `stepup config`
    as being without effect.
    """
    path_package = Path(stepup.report.__file__).parent
    found = set(INKSCAPE_ARGS)
    for path in path_package.walkfiles("*.py"):
        if path.name != "env_vars.py":
            found.update(_string_constants(path.read_text(encoding="utf-8")))
    registered = set(env_vars().env_vars)
    assert found - registered <= set(core_env_vars().env_vars)
    assert registered - found == set()


def test_registry():
    registry = env_vars()
    assert registry.package == "StepUp Report"
    for name, info in registry.env_vars.items():
        assert name.startswith("STEPUP_REPORT_")
        assert not info.secret
        assert not info.overridden


def _stepup_config(path_tmp: Path, env: dict[str, str]) -> subprocess.CompletedProcess:
    """Run `stepup config` in an environment with no other StepUp variables than those given.

    The home directory is replaced, so that a config file of the developer cannot interfere.
    """
    full_env = {name: value for name, value in os.environ.items() if not name.startswith("STEPUP_")}
    full_env.update(HOME=path_tmp, STEPUP_ROOT=path_tmp, **env)
    return subprocess.run(
        [sys.executable, "-m", "stepup.core", "config"],
        cwd=path_tmp,
        env=full_env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )


def test_stepup_config(path_tmp: Path):
    env = {
        "STEPUP_REPORT_NUP_MARGIN": "0",
        "STEPUP_REPORT_TYPST_KEEP_DEPS": "yes",
        "STEPUP_REPORTER_SOCKET": "socket",
    }
    cp = _stepup_config(path_tmp, env)
    assert cp.returncode == 0, cp.stdout + cp.stderr
    assert (
        "# StepUp Report environment variables:\n"
        '#   STEPUP_REPORT_NUP_MARGIN = "0"\n'
        '#   STEPUP_REPORT_TYPST_KEEP_DEPS = "yes"\n'
    ) in cp.stdout
    assert "ERROR" not in cp.stdout
    assert "not prefixed" not in cp.stdout


def test_stepup_config_invalid(path_tmp: Path):
    env = {
        "STEPUP_REPORT_NUP_NROW": "0",
        "STEPUP_REPORT_TECTONIC_ARGS": "'unbalanced",
        "STEPUP_REPORT_TYPST_KEEP_DEPS": "maybe",
    }
    cp = _stepup_config(path_tmp, env)
    assert cp.returncode != 0
    assert '#   STEPUP_REPORT_NUP_NROW = "0"  <-- ERROR: ' in cp.stdout
    assert "#   STEPUP_REPORT_TECTONIC_ARGS = " in cp.stdout
    assert '#   STEPUP_REPORT_TYPST_KEEP_DEPS = "maybe"  <-- ERROR: ' in cp.stdout
    assert cp.stdout.count("<-- ERROR") == 3
