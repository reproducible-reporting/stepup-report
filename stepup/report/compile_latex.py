# SPDX-FileCopyrightText: 2024 Toon Verstraelen <Toon.Verstraelen@UGent.be>
# SPDX-License-Identifier: LGPL-3.0-or-later
"""StepUp Report wrapper for LaTeX."""

import argparse
import shlex
import sys
from collections.abc import Sequence

from stepup.core.api import amend, get_amended_info, getenv
from stepup.core.extapi import filter_dependencies, run_subprocess
from stepup.core.hash import compute_file_digest
from stepup.core.path import Path

from .bibtex_log import parse_bibtex_log
from .latex_deps import scan_latex_deps
from .latex_log import parse_latex_log
from .step_info import write_step_info

__all__ = ("main",)


def main(argv: Sequence[str] | None = None) -> None:
    """Main program."""
    args = parse_args(argv)

    workdir, fn_tex = args.path_tex.splitpath()
    workdir = workdir.normpath()
    if not fn_tex.endswith(".tex"):
        raise ValueError("The LaTeX source must have extension .tex")
    # LaTeX runs in `workdir`, where it only needs `stem`.
    # Paths in this process are relative to the current directory and use `path_stem`.
    stem = fn_tex[:-4]
    path_stem = (workdir / stem).normpath()
    path_aux = Path(f"{path_stem}.aux")
    path_bbl = Path(f"{path_stem}.bbl")

    # Remove existing outputs from a previous run,
    # which could potentially conflict with the new tex source files.
    # In 99% of the cases, this is not a problem,
    # but sometimes LaTeX chokes on remnants in old outputs.
    exts_to_remove = ["log", "aux", "blg", "fls", "out", "toc", "nlo", "synctex"]
    if args.run_bibtex:
        exts_to_remove.append("bbl")
    for ext in exts_to_remove:
        Path(f"{path_stem}.{ext}").remove_p()

    inp, bib, out, vol = scan_latex_deps(args.path_tex, do_amend=False)

    if args.latex is None:
        args.latex = getenv("STEPUP_REPORT_LATEX", "pdflatex")

    if len(bib) == 0:
        amend(inp=inp, out=out, vol=vol)
    elif args.run_bibtex:
        amend(inp=inp + bib, out=[path_bbl, *out], vol=vol)
    else:
        amend(inp=[*inp, path_bbl], out=out, vol=vol)

    aux_digest_hist = []
    if len(bib) > 0 and args.run_bibtex:
        if args.bibtex is None:
            args.bibtex = getenv("STEPUP_REPORT_BIBTEX", "bibtex")

        # Run LaTeX once to generate the .aux file
        cp = run_subprocess(
            f"{shlex.quote(args.latex)} -recorder -interaction=errorstopmode -draftmode {stem}",
            workdir=workdir,
            check=False,
        )
        if cp.returncode != 0:
            path_log = Path(f"{path_stem}.log")
            error_info = parse_latex_log(path_log)
            error_info.print(path_log)
            sys.exit(1)

        aux_digest_hist.append(compute_file_digest(path_aux))

        cp = run_subprocess(f"{shlex.quote(args.bibtex)} {stem}", workdir=workdir, check=False)
        if cp.returncode != 0:
            path_blg = Path(f"{path_stem}.blg")
            error_info = parse_bibtex_log(path_blg)
            error_info.print(path_blg)
            sys.exit(1)

    # Keep running LaTeX until the .aux file converges.
    for _ in range(args.maxrep):
        cp = run_subprocess(
            f"{shlex.quote(args.latex)} -recorder -interaction=errorstopmode {stem}",
            workdir=workdir,
            check=False,
        )
        path_log = Path(f"{path_stem}.log")
        error_info = parse_latex_log(path_log)
        if cp.returncode != 0:
            error_info.print(path_log)
            sys.exit(1)
        aux_digest_hist.append(compute_file_digest(path_aux))
        if len(aux_digest_hist) > 1 and aux_digest_hist[-1] == aux_digest_hist[-2]:
            break
    else:
        print(
            f"\033[1;31;40mAux file did not converge in {args.maxrep} iterations!\033[0;0m",
            file=sys.stderr,
        )
        print(path_aux, file=sys.stderr)
        for digest in aux_digest_hist:
            print(digest.hex(), file=sys.stderr)
        sys.exit(1)

    # Look for input files and output files from the fls file.
    # Relative paths in the fls file are relative to `workdir`.
    # The files already known from scanning the sources are skipped.
    amended = get_amended_info()
    path_fls = Path(f"{path_stem}.fls")
    skip = {
        *amended.inp,
        *amended.out,
        Path(f"{path_stem}.tex"),
        path_aux,
        Path(f"{path_stem}.pdf"),
    }
    if args.step_info is not None:
        skip.add(args.step_info.normpath())
    fls_inp = set()
    fls_vol = set()
    with open(path_fls, encoding="utf-8") as fh:
        for line in fh:
            if line.startswith("INPUT "):
                path = (workdir / line[6:].strip()).normpath()
                if path not in skip:
                    fls_inp.add(path)
            elif line.startswith("OUTPUT "):
                path = (workdir / line[7:].strip()).normpath()
                if path not in skip:
                    fls_vol.add(path)
    fls_inp.difference_update(fls_vol)
    # Both inputs and outputs must be filtered
    # because, strangely, LaTeX sometimes outputs files in the weirdest places,
    # e.g. in the TEXMF tree.
    amend(inp=filter_dependencies(fls_inp), vol=filter_dependencies(fls_vol))

    if args.step_info is not None:
        write_step_info(args.step_info, exclude=[path_fls])


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        prog="sr-compile-latex",
        description="Compile a LaTeX document and extract input and output info.",
    )
    parser.add_argument("path_tex", type=Path, help="The main LaTeX source file.")
    parser.add_argument(
        "-m",
        "--maxrep",
        default=5,
        type=int,
        help="The maximum number of LaTeX recompilations (not including the one for BibTeX).",
    )
    parser.add_argument(
        "--latex",
        help="The LaTeX executable. "
        "The default is ${STEPUP_REPORT_LATEX} or pdflatex if the variable is not defined.",
    )
    parser.add_argument(
        "--run-bibtex",
        dest="run_bibtex",
        default=False,
        action="store_true",
        help="Run bibtex.",
    )
    parser.add_argument(
        "--bibtex",
        help="The BibTeX executable. "
        "The default is ${STEPUP_REPORT_BIBTEX} or bibtex if the variable is not defined.",
    )
    parser.add_argument(
        "--step-info",
        type=Path,
        help="Write a step info file with the inputs and outputs of the step, "
        "except for the fls file, useful for archiving.",
    )
    return parser.parse_args(argv)


if __name__ == "__main__":
    sys.exit(main())
