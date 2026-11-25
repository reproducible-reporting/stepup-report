# SPDX-FileCopyrightText: 2024 Toon Verstraelen <Toon.Verstraelen@UGent.be>
# SPDX-License-Identifier: LGPL-3.0-or-later
"""Raster all pages in a PDF, into a new PDF or into PNG files.

A rasterized PDF is mainly intended to impede (the quality of) unauthorized copies.
"""

import argparse
import sys
from collections.abc import Sequence

import pymupdf

from stepup.core.api import amend, getenv

__all__ = ("main", "raster_pdf", "raster_png")


PAGE_PLACEHOLDERS = ("{p}", "{0p}", "{t}")
"""Placeholders in the name of a PNG output, which are replaced for each page.

They have the same meaning as in the output name of Typst:
`{p}` is the page number, starting from 1,
`{0p}` is the page number padded with zeros to the width of the number of pages,
and `{t}` is the number of pages.
"""


def main(argv: Sequence[str] | None = None):
    """Main program."""
    args = parse_args(argv)
    if args.resolution is None:
        args.resolution = int(getenv("STEPUP_REPORT_RASTER_RESOLUTION", "100"))
    if args.path_out.endswith(".png"):
        if args.quality is not None:
            raise ValueError("The JPEG quality cannot be used with PNG output.")
        paths_png = raster_png(args.path_inp, args.path_out, args.resolution)
        if any(placeholder in args.path_out for placeholder in PAGE_PLACEHOLDERS):
            amend(out=paths_png)
    else:
        if args.quality is None:
            args.quality = int(getenv("STEPUP_REPORT_RASTER_QUALITY", "50"))
        raster_pdf(args.path_inp, args.path_out, args.resolution, args.quality)
    return 0


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        prog="sr-raster-pdf", description="Raster a PDF file, into a new PDF or PNG files."
    )
    parser.add_argument("path_inp", help="The input PDF file.")
    parser.add_argument(
        "path_out",
        help="The output PDF or PNG file. "
        "The name of a PNG file may contain the page placeholders {p}, {0p} and {t}, "
        "and it must contain {p} or {0p} when the input has more than one page.",
    )
    parser.add_argument("-r", "--resolution", type=int, help="Bitmap resolution")
    parser.add_argument("-q", "--quality", type=int, help="JPEG quality, only for PDF output")
    return parser.parse_args(argv)


def raster_pdf(path_inp: str, path_out: str, resolution: int, quality: int):
    """Convert a PDF into a rasterized version."""
    if not path_inp.endswith(".pdf"):
        raise ValueError(f"The input must have a `.pdf` extension, got: {path_inp}")
    if not path_out.endswith(".pdf"):
        raise ValueError(f"The output must have a `.pdf` extension, got: {path_out}")
    if resolution <= 0:
        raise ValueError(f"The resolution must be strictly positive, got: {resolution}")
    with pymupdf.open(path_inp) as src:
        dst = pymupdf.open()
        for src_page in src:
            src_page.wrap_contents()
            if src_page.rotation in (90, 270):
                height, width = src_page.mediabox_size
            else:
                width, height = src_page.mediabox_size
            pix = src_page.get_pixmap(dpi=resolution)
            stream = pix.tobytes(output="jpg", jpg_quality=quality)
            dst_page = dst.new_page(-1, width, height)
            dst_page.insert_image(dst_page.rect, stream=stream)
        dst.save(path_out, garbage=4, deflate=True, no_new_id=True)


def raster_png(path_inp: str, path_out: str, resolution: int) -> list[str]:
    """Render each page of a PDF into a PNG file.

    Parameters
    ----------
    path_inp
        The input PDF file.
    path_out
        The output PNG file, whose name may contain the placeholders in `PAGE_PLACEHOLDERS`.
        It must contain `{p}` or `{0p}` when the input has more than one page.
    resolution
        The resolution of the PNG files in dots per inch.

    Returns
    -------
    paths_png
        The PNG files that were written, in the order of the pages.
    """
    if not path_inp.endswith(".pdf"):
        raise ValueError(f"The input must have a `.pdf` extension, got: {path_inp}")
    if not path_out.endswith(".png"):
        raise ValueError(f"The output must have a `.png` extension, got: {path_out}")
    if resolution <= 0:
        raise ValueError(f"The resolution must be strictly positive, got: {resolution}")
    paths_png = []
    with pymupdf.open(path_inp) as src:
        npage = len(src)
        if npage > 1 and not ("{p}" in path_out or "{0p}" in path_out):
            raise ValueError(
                f"The input has {npage} pages, so the output must contain {{p}} or {{0p}}, "
                f"got: {path_out}"
            )
        for ipage, page in enumerate(src, 1):
            path_png = (
                path_out.replace("{p}", str(ipage))
                .replace("{0p}", str(ipage).zfill(len(str(npage))))
                .replace("{t}", str(npage))
            )
            page.get_pixmap(dpi=resolution).save(path_png)
            paths_png.append(path_png)
    return paths_png


if __name__ == "__main__":
    sys.exit(main())
