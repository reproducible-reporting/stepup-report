# SPDX-FileCopyrightText: 2026 Toon Verstraelen <Toon.Verstraelen@UGent.be>
# SPDX-License-Identifier: LGPL-3.0-or-later
"""Unit tests for stepup.report.raster_pdf."""

import pymupdf
import pytest

from stepup.core.path import Path
from stepup.report.raster_pdf import raster_png


def make_pdf(path_pdf: Path, npage: int):
    with pymupdf.open() as doc:
        for ipage in range(npage):
            page = doc.new_page(width=100, height=100)
            page.insert_text((10, 50), f"Page {ipage + 1}")
        doc.save(path_pdf)


def test_raster_png_single(path_tmp: Path):
    path_pdf = path_tmp / "doc.pdf"
    make_pdf(path_pdf, 1)
    path_png = path_tmp / "doc.png"
    assert raster_png(path_pdf, path_png, 72) == [path_png]
    with pymupdf.open(path_png) as png:
        assert png[0].rect.width == 100


def test_raster_png_placeholders(path_tmp: Path):
    path_pdf = path_tmp / "doc.pdf"
    make_pdf(path_pdf, 10)
    paths_png = raster_png(path_pdf, path_tmp / "doc-{0p}-{p}-{t}.png", 36)
    assert paths_png[0] == path_tmp / "doc-01-1-10.png"
    assert paths_png[-1] == path_tmp / "doc-10-10-10.png"
    assert all(Path(path_png).is_file() for path_png in paths_png)


def test_raster_png_multi_without_placeholder(path_tmp: Path):
    path_pdf = path_tmp / "doc.pdf"
    make_pdf(path_pdf, 2)
    with pytest.raises(ValueError, match="2 pages"):
        raster_png(path_pdf, path_tmp / "doc-{t}.png", 36)
