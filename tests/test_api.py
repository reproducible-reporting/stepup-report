# SPDX-FileCopyrightText: 2024 Toon Verstraelen <Toon.Verstraelen@UGent.be>
# SPDX-License-Identifier: LGPL-3.0-or-later
"""Unit tests for stepup.report.api."""

import inspect
import pathlib
import shlex

import pytest

from stepup.core.path import PathError, StrPath
from stepup.report import api
from stepup.report.api import (
    add_notes_pdf,
    cat_pdf,
    check_hrefs,
    compile_latex,
    compile_tectonic,
    compile_typst,
    convert_inkscape,
    convert_markdown,
    convert_weasyprint,
    diff_latex,
    flatten_latex,
    nup_pdf,
    raster_pdf,
    sanitize_bibtex,
)
from stepup.report.convert_markdown import parse_args as parse_args_markdown


@pytest.mark.parametrize("name", api.__all__)
def test_keyword_only_options(name: str):
    signature = inspect.signature(getattr(api, name))
    for option in "optional", "resources", "duration", "step_info":
        parameter = signature.parameters.get(option)
        if parameter is not None:
            assert parameter.kind == inspect.Parameter.KEYWORD_ONLY


def test_compile_tectonic_dest_file():
    with pytest.raises(ValueError, match="must be a directory"):
        compile_tectonic("paper.tex", "other.pdf")


@pytest.fixture
def run_calls(monkeypatch) -> list[tuple[str, dict]]:
    """Replace `run()` in the API module by a function that records the commands and arguments."""
    calls = []

    def fake_run(command, **kwargs):
        calls.append((command, kwargs))
        return command

    monkeypatch.setattr("stepup.report.api.run", fake_run)
    return calls


def test_compile_latex_step_info(run_calls: list[tuple[str, dict]]):
    compile_latex("paper.tex", step_info="info dir/paper.json")
    ((command, kwargs),) = run_calls
    assert command == "sr-compile-latex paper.tex --run-bibtex --step-info='info dir/paper.json'"
    assert kwargs["out"] == ["paper.pdf", "paper.aux", "paper.fls", "info dir/paper.json"]


def test_compile_tectonic_step_info(run_calls: list[tuple[str, dict]]):
    compile_tectonic("paper.tex", step_info="paper.json")
    ((command, kwargs),) = run_calls
    assert command == "sr-compile-tectonic --step-info=paper.json paper.tex"
    assert kwargs["out"] == ["paper.pdf", "paper.json"]


def test_compile_typst_step_info(run_calls: list[tuple[str, dict]]):
    compile_typst("doc.typ", step_info="doc.json")
    ((command, kwargs),) = run_calls
    assert command == "sr-compile-typst --step-info=doc.json doc.typ"
    assert kwargs["out"] == ["doc.pdf", "doc.json"]


def test_compile_latex_without_step_info(run_calls: list[tuple[str, dict]]):
    compile_latex("paper.tex")
    ((command, kwargs),) = run_calls
    assert "--step-info" not in command
    assert kwargs["out"] == ["paper.pdf", "paper.aux", "paper.fls"]


def test_diff_latex_default_args(run_calls: list[tuple[str, dict]], monkeypatch):
    monkeypatch.delenv("STEPUP_REPORT_LATEXDIFF_ARGS", raising=False)
    diff_latex("old.tex", "new.tex", "diff.tex")
    ((command, _),) = run_calls
    assert command.startswith("latexdiff --append-context2cmd=abstract,")
    assert command.endswith(" old.tex new.tex --no-label > diff.tex")


def test_diff_latex_env_args(run_calls: list[tuple[str, dict]], monkeypatch):
    monkeypatch.setenv("STEPUP_REPORT_LATEXDIFF_ARGS", "--type=CFONT '--exclude-textcmd=a b'")
    diff_latex("old.tex", "new.tex", "diff.tex")
    ((command, _),) = run_calls
    assert command == (
        "latexdiff --type=CFONT '--exclude-textcmd=a b' old.tex new.tex --no-label > diff.tex"
    )


def test_diff_latex_explicit_args(run_calls: list[tuple[str, dict]], monkeypatch):
    monkeypatch.setenv("STEPUP_REPORT_LATEXDIFF_ARGS", "--type=CFONT")
    diff_latex("old.tex", "new.tex", "diff.tex", latexdiff_args=[])
    ((command, _),) = run_calls
    assert command == "latexdiff old.tex new.tex --no-label > diff.tex"


def test_diff_latex_dest_dir(run_calls: list[tuple[str, dict]]):
    diff_latex("old/paper.tex", "new/paper.tex", "diff/", latexdiff_args=[])
    ((command, kwargs),) = run_calls
    assert command == "latexdiff old/paper.tex new/paper.tex --no-label > diff/paper.tex"
    assert kwargs["out"] == "diff/paper.tex"


def test_diff_latex_dest_extension():
    with pytest.raises(ValueError, match="extension"):
        diff_latex("old.bbl", "new.bbl", "diff.tex")


def test_add_notes_pdf_dest_dir(run_calls: list[tuple[str, dict]]):
    add_notes_pdf("doc.pdf", "notes.pdf", "out/")
    ((command, kwargs),) = run_calls
    assert command == "sr-add-notes-pdf doc.pdf notes.pdf out/doc.pdf"
    assert kwargs["out"] == "out/doc.pdf"


def test_cat_pdf_dest_dir():
    with pytest.raises(ValueError, match=r"\.pdf"):
        cat_pdf(["a.pdf", "b.pdf"], "out/")


def test_check_hrefs_config(run_calls: list[tuple[str, dict]]):
    check_hrefs("doc.md", path_config="hrefs.yaml")
    ((command, kwargs),) = run_calls
    assert command == "sr-check-hrefs doc.md -c hrefs.yaml"
    assert kwargs["inp"] == ["doc.md", "hrefs.yaml"]


def test_convert_inkscape_default(run_calls: list[tuple[str, dict]]):
    convert_inkscape("fig.svg")
    ((command, kwargs),) = run_calls
    assert command == "sr-convert-inkscape fig.svg fig.pdf"
    assert kwargs["out"] == ["fig.pdf"]


def test_convert_inkscape_png(run_calls: list[tuple[str, dict]]):
    convert_inkscape("fig.svg", "out/fig.png", inkscape_args=["-d", "300"], step_info="fig.json")
    ((command, kwargs),) = run_calls
    assert command == "sr-convert-inkscape fig.svg out/fig.png --step-info=fig.json -- -d 300"
    assert kwargs["out"] == ["out/fig.png", "fig.json"]


def test_convert_inkscape_wrong_extension():
    with pytest.raises(PathError):
        convert_inkscape("fig.svg", "fig.jpg")


@pytest.mark.parametrize(
    ("paths_css", "expected"),
    [
        ("page.css", ["page.css"]),
        (pathlib.Path("page.css"), ["page.css"]),
        (["a.css", pathlib.Path("b c.css")], ["a.css", "b c.css"]),
    ],
)
def test_convert_markdown_css(
    run_calls: list[tuple[str, dict]], paths_css: StrPath | list[StrPath], expected: list[str]
):
    convert_markdown("doc.md", paths_css=paths_css)
    ((command, kwargs),) = run_calls
    assert kwargs["inp"] == ["doc.md", *expected]
    args = parse_args_markdown(shlex.split(command)[1:])
    assert args.css == expected


def test_convert_markdown_without_css(run_calls: list[tuple[str, dict]]):
    convert_markdown("doc.md")
    ((command, kwargs),) = run_calls
    assert command == "sr-convert-markdown doc.md doc.html"
    assert kwargs["inp"] == ["doc.md"]


def test_convert_weasyprint_step_info(run_calls: list[tuple[str, dict]]):
    convert_weasyprint("doc.html", step_info="doc.json")
    ((command, kwargs),) = run_calls
    assert command == "sr-convert-weasyprint doc.html doc.pdf --step-info=doc.json"
    assert kwargs["out"] == ["doc.pdf", "doc.json"]


@pytest.mark.parametrize(
    ("dest", "path_flat"),
    [(None, "sub/paper-flat.tex"), ("flat/", "flat/paper.tex"), ("flat.tex", "flat.tex")],
)
def test_flatten_latex_dest(run_calls: list[tuple[str, dict]], dest: str | None, path_flat: str):
    flatten_latex("sub/paper.tex", dest)
    ((command, kwargs),) = run_calls
    assert command == f"sr-flatten-latex sub/paper.tex {path_flat}"
    assert kwargs["out"] == path_flat


def test_nup_pdf_dest_dir(run_calls: list[tuple[str, dict]]):
    nup_pdf("doc.pdf", "nup/")
    ((command, kwargs),) = run_calls
    assert command == "sr-nup-pdf doc.pdf nup/doc.pdf"
    assert kwargs["out"] == "nup/doc.pdf"


def test_raster_pdf_png(run_calls: list[tuple[str, dict]]):
    raster_pdf("doc.pdf", "doc.png")
    ((command, kwargs),) = run_calls
    assert command == "sr-raster-pdf doc.pdf doc.png"
    assert kwargs["out"] == ["doc.png"]


def test_raster_pdf_png_placeholders(run_calls: list[tuple[str, dict]]):
    raster_pdf("doc.pdf", "doc-{p}.png", resolution=50)
    ((command, kwargs),) = run_calls
    assert command == "sr-raster-pdf doc.pdf 'doc-{p}.png' -r 50"
    assert kwargs["out"] == []


def test_raster_pdf_png_quality():
    with pytest.raises(ValueError, match="quality"):
        raster_pdf("doc.pdf", "doc.png", quality=80)


def test_sanitize_bibtex_in_place(run_calls: list[tuple[str, dict]]):
    sanitize_bibtex("refs.bib", path_config="bibsane.yaml")
    ((command, kwargs),) = run_calls
    assert command == "sr-bibsane refs.bib --config=bibsane.yaml"
    assert kwargs["out"] == []


def test_sanitize_bibtex_dest(run_calls: list[tuple[str, dict]]):
    sanitize_bibtex("refs.bib", "clean/")
    ((command, kwargs),) = run_calls
    assert command == "sr-bibsane refs.bib --out=clean/refs.bib"
    assert kwargs["out"] == ["clean/refs.bib"]
