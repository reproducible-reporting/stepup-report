# SPDX-FileCopyrightText: 2024 Toon Verstraelen <Toon.Verstraelen@UGent.be>
# SPDX-License-Identifier: LGPL-3.0-or-later
"""Application programming interface for StepUp Report."""

import os
import shlex
from collections.abc import Collection

from stepup.core.api import getenv, run, shq, subs_env_vars
from stepup.core.path import Path, StrPath, coerce_paths, coerce_str, make_path_out
from stepup.core.stepinfo import StepInfo

__all__ = (
    "add_notes_pdf",
    "cat_pdf",
    "check_hrefs",
    "compile_latex",
    "compile_tectonic",
    "compile_typst",
    "convert_inkscape",
    "convert_markdown",
    "convert_weasyprint",
    "diff_latex",
    "flatten_latex",
    "nup_pdf",
    "raster_pdf",
    "sanitize_bibtex",
    "unplot",
)


def add_notes_pdf(
    path_pdf: StrPath,
    path_notes: StrPath,
    dest: StrPath,
    *,
    optional: bool = False,
    resources: dict[str, int] | str | None = None,
    duration: float | None = None,
) -> StepInfo:
    """Add a notes page at every even page of a PDF file.

    Parameters
    ----------
    path_pdf
        The original PDF document without notes pages.
    path_notes
        A single-page PDF document with a page suitable for taking notes.
    dest
        The output PDF with notes pages inserted, or a directory with a trailing slash.
        In a directory, the output has the same name as `path_pdf`.
    optional
        If `True`, the step is only executed when needed by other steps.
    resources
        Named resources required to run this step, e.g. `{"gpu": 1}`.
        See `stepup.core.api.step()` for details.
    duration
        An initial estimate of the step's wall time in seconds.
        See `stepup.core.api.step()` for details.

    Returns
    -------
    step_info
        Holds relevant information of the step, useful for defining follow-up steps.
    """
    path_out = make_path_out(path_pdf, dest, ".pdf")
    return run(
        f"sr-add-notes-pdf {shq(path_pdf)} {shq(path_notes)} {shq(path_out)}",
        inp=[path_pdf, path_notes],
        out=path_out,
        optional=optional,
        resources=resources,
        duration=duration,
    )


def cat_pdf(
    paths_pdf: Collection[StrPath],
    dest: StrPath,
    *,
    insert_blank: bool = False,
    optional: bool = False,
    resources: dict[str, int] | str | None = None,
    duration: float | None = None,
) -> StepInfo:
    """Concatenate the pages of multiple PDFs into one document.

    Parameters
    ----------
    paths_pdf
        The input PDF files.
    dest
        The concatenated PDF.
    insert_blank
        Insert a blank page after a PDF with an odd number of pages.
        The last page of each PDF is used to determine the size of the added blank page.
    optional
        If `True`, the step is only executed when needed by other steps.
    resources
        Named resources required to run this step, e.g. `{"gpu": 1}`.
        See `stepup.core.api.step()` for details.
    duration
        An initial estimate of the step's wall time in seconds.
        See `stepup.core.api.step()` for details.

    Returns
    -------
    step_info
        Holds relevant information of the step, useful for defining follow-up steps.
    """
    if not coerce_str(dest).endswith(".pdf"):
        raise ValueError(f"The output of cat_pdf must be a file with extension .pdf, got {dest}.")
    parts = [f"sr-cat-pdf {shq(paths_pdf)} {shq(dest)}"]
    if insert_blank:
        parts.append("--insert-blank")
    return run(
        " ".join(parts),
        inp=paths_pdf,
        out=dest,
        optional=optional,
        resources=resources,
        duration=duration,
    )


def check_hrefs(
    path_src: StrPath,
    *,
    path_config: StrPath | None = None,
    resources: dict[str, int] | str | None = None,
    duration: float | None = None,
) -> StepInfo:
    """Check hyper references in a Markdown, HTML or PDF file.

    Parameters
    ----------
    path_src
        The source Markdown, HTML or PDF to check.
    path_config
        The configuration file.
        Defaults to `${STEPUP_REPORT_CHECK_HREFS_CONFIG}` variable
        or `check_hrefs.yaml` if it is not set.
    resources
        Named resources required to run this step, e.g. `{"gpu": 1}`.
        See `stepup.core.api.step()` for details.
    duration
        An initial estimate of the step's wall time in seconds.
        See `stepup.core.api.step()` for details.

    Returns
    -------
    step_info
        Holds relevant information of the step, useful for defining follow-up steps.
    """
    parts = [f"sr-check-hrefs {shq(path_src)}"]
    paths_inp = [path_src]
    if path_config is not None:
        parts.append(f"-c {shq(path_config)}")
        paths_inp.append(path_config)
    return run(" ".join(parts), inp=paths_inp, resources=resources, duration=duration)


def compile_latex(
    path_tex: StrPath,
    *,
    run_bibtex: bool = True,
    maxrep: int = 5,
    workdir: StrPath = "./",
    latex: StrPath | None = None,
    bibtex: StrPath | None = None,
    step_info: StrPath | None = None,
    optional: bool = False,
    resources: dict[str, int] | str | None = None,
    duration: float | None = None,
) -> StepInfo:
    """Create a step for the compilation of a LaTeX source.

    Parameters
    ----------
    path_tex
        The main tex source file.
        This argument may contain environment variables.
    run_bibtex
        By default, when bib files are used, BibTeX is invoked.
        This can be overruled by setting this argument to False,
        which is useful when recompiling sources with fixed bbl files.
    maxrep
        The maximum number of repetitions of the LaTeX command
        in case the aux file keeps changing.
    workdir
        The working directory where the LaTeX command must be executed.
    latex
        Path to the LaTeX executable.
        Note that only PDF-producing LaTeX compilers are supported:
        `pdflatex`, `xelatex` or `lualatex`.
        Defaults to `${STEPUP_REPORT_LATEX}` variable or `pdflatex` if the variable is unset.
    bibtex
        Path to the BibTeX executable.
        Defaults to `${STEPUP_REPORT_BIBTEX}` variable or `bibtex` if the variable is unset.
    step_info
        A JSON file to which the dependencies of the step are written
        when the step succeeds, in the format of `dump_step_info()` of StepUp Core.
        It lists the main LaTeX source, the `.aux` and `.pdf` outputs,
        the files found by scanning the LaTeX sources,
        including those declared with `%REPREP inp` and `%REPREP out`,
        the bibliography files and the `.bbl` file.
        The `.bbl` file is an output when BibTeX runs and an input otherwise.
        It also lists the files that LaTeX reports in the `.fls` file,
        such as local class and style files,
        as far as `${STEPUP_PATH_FILTER}` retains them.
        By default, this excludes the files outside `${STEPUP_ROOT}`,
        such as those of the LaTeX distribution.
        Volatile files and the `.fls` file itself are not listed.
        The file is an output of the step, but it does not list itself.
        Pass it to `make_inventory()` of StepUp Data to archive these files,
        e.g. to send the sources of the document to a journal.
    optional
        If `True`, the step is only executed when needed by other steps.
    resources
        Named resources required to run this step, e.g. `{"gpu": 1}`.
        See `stepup.core.api.step()` for details.
    duration
        An initial estimate of the step's wall time in seconds.
        See `stepup.core.api.step()` for details.

    Returns
    -------
    step_info
        Holds relevant information of the step, useful for defining follow-up steps.

    Notes
    -----
    The LaTeX source is compiled with the `sr-compile-latex` command,
    which can detect dependencies on other files
    by scanning for `\\input`, `\\include`, `\\includegraphics`, etc.
    Due to the complexity of LaTeX, the dependency scanning is not perfect.
    You can manually specify dependencies in the LaTeX source with the following comments:

    -  `%REPREP inp inp_path`
    -  `%REPREP out out_path`
    -  `%REPREP vol vol_path`

    When any of these paths is a relative path,
    it is interpreted in the same way as the LaTeX compiler would resolve it.
    You can also hide lines from the dependency scanner
    by adding `%REPREP ignore` at the end of a line.
    """
    with subs_env_vars() as subs:
        su_workdir = subs(workdir)
        path_tex = subs(path_tex, su_workdir)
        step_info = subs(step_info, su_workdir)
    if not path_tex.endswith(".tex"):
        raise ValueError(f"The input of the latex command must end with .tex, got {path_tex}.")

    stem = path_tex[:-4]
    path_pdf = f"{stem}.pdf"

    parts = ["sr-compile-latex", shq(path_tex)]
    paths_inp = [path_tex]
    paths_out = [path_pdf, f"{stem}.aux", f"{stem}.fls"]
    if maxrep != 5:
        parts.append(f"--maxrep={maxrep}")
    if latex is not None:
        parts.append(f"--latex={shq(latex)}")
    if run_bibtex:
        parts.append("--run-bibtex")
        if bibtex is not None:
            parts.append(f"--bibtex={shq(bibtex)}")
    if step_info is not None:
        parts.append(f"--step-info={shq(step_info)}")
        paths_out.append(step_info)
    return run(
        " ".join(parts),
        inp=paths_inp,
        out=paths_out,
        workdir=workdir,
        optional=optional,
        resources=resources,
        duration=duration,
    )


def compile_tectonic(
    path_tex: StrPath,
    dest: StrPath | None = None,
    *,
    workdir: StrPath = "./",
    tectonic: StrPath | None = None,
    keep_deps: bool | None = None,
    tectonic_args: Collection[str] = (),
    step_info: StrPath | None = None,
    optional: bool = False,
    resources: dict[str, int] | str | None = None,
    duration: float | None = None,
) -> StepInfo:
    """Create a step for the compilation of a LaTeX source with Tectonic.

    !!! warning

        This feature is only tested with Tectonic 0.17

        Support for Tectonic in StepUp Report is experimental.
        Expect breaking changes in future releases.

    Parameters
    ----------
    path_tex
        The main LaTeX source file.
        This argument may contain environment variables.
    dest
        Output directory, with a trailing slash.
        If `None`, the PDF is written in the directory of the LaTeX source.
    workdir
        The working directory where the LaTeX command must be executed.
    tectonic
        Path to the Tectonic executable.
        Defaults to `${STEPUP_REPORT_TECTONIC}` variable or `tectonic` if the variable is unset.
    keep_deps
        If `True`, the dependency file is kept after the compilation.
        When not set, the `sr-compile-tectonic` command will use the value
        of the environment variable `STEPUP_REPORT_TECTONIC_KEEP_DEPS` or default to `False`
        if the variable is not defined.
    tectonic_args
        Additional arguments for tectonic.
        The defaults is `${STEPUP_REPORT_TECTONIC_ARGS}`, if the environment variable is defined.
    step_info
        A JSON file to which the dependencies of the step are written
        when the step succeeds, in the format of `dump_step_info()` of StepUp Core.
        It lists the main LaTeX source, the PDF,
        and the local files read by Tectonic, as reported in its dependency file,
        but not the dependency file itself when it is kept.
        The file is an output of the step, but it does not list itself.
        Pass it to `make_inventory()` of StepUp Data to archive these files,
        e.g. to send the sources of the document to a journal.
    optional
        If `True`, the step is only executed when needed by other steps.
    resources
        Named resources required to run this step, e.g. `{"gpu": 1}`.
        See `stepup.core.api.step()` for details.
    duration
        An initial estimate of the step's wall time in seconds.
        See `stepup.core.api.step()` for details.

    Returns
    -------
    step_info
        Holds relevant information of the step, useful for defining follow-up steps.
    """
    with subs_env_vars() as subs:
        su_workdir = subs(workdir)
        path_tex = subs(path_tex, su_workdir)
        step_info = subs(step_info, su_workdir)
        dest = subs(dest, su_workdir)
    if not path_tex.endswith(".tex"):
        raise ValueError(f"The input of the tectonic command must end with .tex, got {path_tex}.")
    if not (dest is None or dest.endswith("/")):
        raise ValueError(
            f"The dest of the tectonic command must be a directory ending with /, got {dest}."
        )
    path_out = make_path_out(path_tex, dest, ".pdf")

    stem = path_tex[:-4]
    parts = ["sr-compile-tectonic"]
    if tectonic is not None:
        parts.append(f"--tectonic={shq(tectonic)}")
    if dest is not None:
        parts.append(f"--outdir={shq(dest)}")
    paths_out = [path_out]
    if keep_deps is not None:
        if keep_deps:
            parts.append("--keep-deps")
            paths_out.append(f"{stem}.dep")
        else:
            parts.append("--no-keep-deps")
    if step_info is not None:
        parts.append(f"--step-info={shq(step_info)}")
        paths_out.append(step_info)
    parts.append(shq(path_tex))
    path_inp = [path_tex]
    if len(tectonic_args) > 0:
        parts.append("--")
        parts.extend(shlex.quote(tectonic_arg) for tectonic_arg in tectonic_args)

    return run(
        " ".join(parts),
        inp=path_inp,
        out=paths_out,
        workdir=workdir,
        optional=optional,
        resources=resources,
        duration=duration,
    )


def compile_typst(
    path_typ: StrPath,
    dest: StrPath | None = None,
    *,
    inp: StrPath | Collection[StrPath] = (),
    sysinp: dict[str, str | int | float | StrPath] | None = None,
    resolution: int | None = None,
    workdir: StrPath = "./",
    typst: StrPath | None = None,
    keep_deps: bool | None = None,
    typst_args: Collection[str] = (),
    step_info: StrPath | None = None,
    optional: bool = False,
    resources: dict[str, int] | str | None = None,
    duration: float | None = None,
) -> StepInfo:
    """Create a step for the compilation of a Typst source.

    !!! warning

        This feature is expected to work only with typst 0.15.

        Support for Typst in StepUp Report is experimental.
        Expect breaking changes in future releases.
        Some limitations include:

        - SVG figures with references to external SVG images are not processed correctly.
          These images are not rendered, neither are they included in the dep file.
          Tracked upstream in <https://github.com/typst/typst/issues/6858>.

    Parameters
    ----------
    path_typ
        The main typst source file.
        This argument may contain environment variables.
    dest
        Output destination: `None`, a directory or a file.
        For SVG and PNG outputs, this argument must be specified with the desired extension.
        If the output contains any of `{p}`, `{0p}` or `{t}`, the output paths are not
        known a priori and will be amended.
    inp
        Additional files that are inputs to the typst source, e.g. images or other typst files.
        Note that these dependencies are detected automatically after the typst compilation,
        so specifying them here is optional and only improves scheduling efficiency
        when these inputs are the outputs of other steps.
    sysinp
        A dictionary with the input arguments passed to `typst` with `--input key=val`.
        Items are ignored when keys are not strings or when values
        are not of type `str`, `int`, `float`, `path.Path` or `os.PathLike`
        (e.g. `pathlib.Path`).
        If a key is not a valid Python identifier, an exception is raised.
        These parameters are available in the document as `#sys.inputs.key`.
        One may also provide an object, which is converted into a `dict` with the `vars()` built-in.
    resolution
        The resolution of the bitmap in dots per inch (dpi),
        only relevant for PNG output.
    workdir
        The working directory where the LaTeX command must be executed.
    typst
        Path to the Typst executable.
        Defaults to `${STEPUP_REPORT_TYPST}` variable or `typst` if the variable is unset.
    keep_deps
        If `True`, the dependency file is kept after the compilation.
        When not set, the `sr-compile-typst` command will use the value
        of the environment variable `STEPUP_REPORT_TYPST_KEEP_DEPS` or default to `False`
        if the variable is not defined.
    typst_args
        Additional arguments for typst.
        The defaults is `${STEPUP_REPORT_TYPST_ARGS}`, if the environment variable is defined.
    step_info
        A JSON file to which the dependencies of the step are written
        when the step succeeds, in the format of `dump_step_info()` of StepUp Core.
        It lists the main Typst source, the files in `inp`, the outputs,
        and the local files read by Typst, as reported in its dependency file,
        but not the dependency file itself when it is kept.
        The file is an output of the step, but it does not list itself.
        Pass it to `make_inventory()` of StepUp Data to archive these files,
        e.g. to send the sources of the document to a journal.
    optional
        If `True`, the step is only executed when needed by other steps.
    resources
        Named resources required to run this step, e.g. `{"gpu": 1}`.
        See `stepup.core.api.step()` for details.
    duration
        An initial estimate of the step's wall time in seconds.
        See `stepup.core.api.step()` for details.

    Returns
    -------
    step_info
        Holds relevant information of the step, useful for defining follow-up steps.
    """
    with subs_env_vars() as subs:
        su_workdir = subs(workdir)
        path_typ = subs(path_typ, su_workdir)
        step_info = subs(step_info, su_workdir)
        dest = subs(dest, su_workdir)
    if not path_typ.endswith(".typ"):
        raise ValueError(f"The input of the typst command must end with .typ, got {path_typ}.")
    path_out = make_path_out(path_typ, dest, ".pdf", [".svg", ".png", ".html"])

    stem = path_typ[:-4]
    parts = ["sr-compile-typst"]
    if resolution is not None:
        parts.append(f"--resolution={resolution}")
    if typst is not None:
        parts.append(f"--typst={shq(typst)}")
    paths_out = []
    if not any(x in path_out for x in ("{p}", "{0p}", "{t}")):
        paths_out.append(path_out)
    if keep_deps is not None:
        if keep_deps:
            parts.append("--keep-deps")
            paths_out.append(f"{stem}.deps.json")
        else:
            parts.append("--no-keep-deps")
    if step_info is not None:
        parts.append(f"--step-info={shq(step_info)}")
        paths_out.append(step_info)
    parts.append(shq(path_typ))
    if path_typ[:-4] != path_out[:-4]:
        parts.append(f"--out={shq(path_out)}")
    if sysinp is not None:
        if not isinstance(sysinp, dict):
            sysinp = vars(sysinp)
        if len(sysinp) > 0:
            parts.append("--sysinp")
            for key, val in sysinp.items():
                if not isinstance(key, str):
                    continue
                if not isinstance(val, str | int | float | os.PathLike):
                    continue
                if not key.isidentifier():
                    raise ValueError(f"Invalid sysinp key: {key}")
                val = coerce_str(val) if isinstance(val, Path | os.PathLike) else str(val)
                parts.append(f"{key}={shlex.quote(val)}")
    if len(typst_args) > 0:
        parts.append("--")
        parts.extend(shlex.quote(typst_arg) for typst_arg in typst_args)

    return run(
        " ".join(parts),
        inp=[path_typ, *coerce_paths(inp)],
        out=paths_out,
        workdir=workdir,
        optional=optional,
        resources=resources,
        duration=duration,
    )


DEFAULT_LATEXDIFF_ARGS = (
    "--append-context2cmd=abstract,supplementary,dataavailability,funding,"
    "authorcontributions,conflictsofinterest,abbreviations",
)


def convert_inkscape(
    path_svg: StrPath,
    dest: StrPath | None = None,
    *,
    inkscape: StrPath | None = None,
    inkscape_args: Collection[str] = (),
    step_info: StrPath | None = None,
    optional: bool = False,
    resources: dict[str, int] | str | None = None,
    duration: float | None = None,
) -> StepInfo:
    """Convert an SVG figure to PDF or PNG, detecting dependencies of the SVG on other files.

    Parameters
    ----------
    path_svg
        The input SVG figure.
        It may contain `<image>` tags referring to other files included in the figure.
    dest
        Output destination: `None`, a directory or a file.
        The output is a PDF file, unless `dest` is a file with extension `.png`.
    inkscape
        The path to the inkscape executable.
        Defaults to `${STEPUP_REPORT_INKSCAPE}` variable or `inkscape` if the variable is unset.
    inkscape_args
        Additional arguments to pass to inkscape. E.g. `["-T"]` to convert text to glyphs in PDFs.
        Depending on the extension of the output,
        the default is `${STEPUP_REPORT_INKSCAPE_PDF_ARGS}` or `${STEPUP_REPORT_INKSCAPE_PNG_ARGS}`,
        if the environment variable is defined.
    step_info
        A JSON file to which the dependencies of the step are written
        when the step succeeds, in the format of `dump_step_info()` of StepUp Core.
        It lists the SVG file, the output and the files included in the figure.
        The file is an output of the step, but it does not list itself.
        Pass it to `make_inventory()` of StepUp Data to archive these files.
    optional
        If `True`, the step is only executed when needed by other steps.
    resources
        Named resources required to run this step, e.g. `{"gpu": 1}`.
        See `stepup.core.api.step()` for details.
    duration
        An initial estimate of the step's wall time in seconds.
        See `stepup.core.api.step()` for details.

    Returns
    -------
    step_info
        Holds relevant information of the step, useful for defining follow-up steps.

    Notes
    -----
    Images and other files referenced by the SVG are detected automatically
    and amended as inputs of the step.
    This scan may be a bit slow in case of large files.
    """
    with subs_env_vars() as subs:
        path_svg = subs(path_svg)
        dest = subs(dest)
        step_info = subs(step_info)
    if not path_svg.endswith(".svg"):
        raise ValueError("The SVG file must have extension .svg")
    path_out = make_path_out(path_svg, dest, ".pdf", [".png"])
    parts = ["sr-convert-inkscape", shq(path_svg), shq(path_out)]
    paths_out = [path_out]
    if inkscape is not None:
        parts.append(f"--inkscape={shq(inkscape)}")
    if step_info is not None:
        parts.append(f"--step-info={shq(step_info)}")
        paths_out.append(step_info)
    if len(inkscape_args) > 0:
        parts.append("--")
        parts.extend(shlex.quote(inkscape_arg) for inkscape_arg in inkscape_args)
    return run(
        " ".join(parts),
        inp=path_svg,
        out=paths_out,
        optional=optional,
        resources=resources,
        duration=duration,
    )


def convert_markdown(
    path_md: StrPath,
    dest: StrPath | None = None,
    *,
    paths_css: StrPath | Collection[StrPath] = (),
    optional: bool = False,
    resources: dict[str, int] | str | None = None,
    duration: float | None = None,
) -> StepInfo:
    """Convert a markdown to HTML.

    Parameters
    ----------
    path_md
        The markdown input file.
    dest
        Output destination: `None`, a directory or a file.
    paths_css
        Path or multiple paths of a local CSS file, or a list of multiple such paths,
        to be included in the HTML header.
        Note that one may also specify CSS file in the markdown header.
        Defaults to `${STEPUP_REPORT_MARKDOWN_CSS}` if the variable is set,
        which is interpreted as a list of files separated by `:`, or by `;` on Windows.
    optional
        If `True`, the step is only executed when needed by other steps.
    resources
        Named resources required to run this step, e.g. `{"gpu": 1}`.
        See `stepup.core.api.step()` for details.
    duration
        An initial estimate of the step's wall time in seconds.
        See `stepup.core.api.step()` for details.

    Returns
    -------
    step_info
        Holds relevant information of the step, useful for defining follow-up steps.
    """
    with subs_env_vars() as subs:
        path_md = subs(path_md)
        dest = subs(dest)
    if not path_md.endswith(".md"):
        raise ValueError("The Markdown file must have extension .md")
    path_html = make_path_out(path_md, dest, ".html")
    inp = [path_md]
    parts = ["sr-convert-markdown", shq(path_md), shq(path_html)]
    paths_css = coerce_paths(paths_css)
    if len(paths_css) > 0:
        parts.append(f"--css {shq(paths_css)}")
        inp.extend(paths_css)
    return run(
        " ".join(parts),
        inp=inp,
        out=path_html,
        optional=optional,
        resources=resources,
        duration=duration,
    )


def convert_weasyprint(
    path_html: StrPath,
    dest: StrPath | None = None,
    *,
    weasyprint: StrPath | None = None,
    step_info: StrPath | None = None,
    optional: bool = False,
    resources: dict[str, int] | str | None = None,
    duration: float | None = None,
) -> StepInfo:
    """Convert a HTML document to PDF with WeasyPrint.

    WeasyPrint is not installed with StepUp Report.
    See the installation instructions for how to install it.

    Parameters
    ----------
    path_html
        The HTML input file.
    dest
        Output destination: `None`, a directory or a file.
    weasyprint
        The path to the weasyprint executable.
        Defaults to `${STEPUP_REPORT_WEASYPRINT}` variable or `weasyprint` if the variable is unset.
    step_info
        A JSON file to which the dependencies of the step are written
        when the step succeeds, in the format of `dump_step_info()` of StepUp Core.
        It lists the HTML file, the PDF, and the images and style sheets used by the HTML file.
        The file is an output of the step, but it does not list itself.
        Pass it to `make_inventory()` of StepUp Data to archive these files.
    optional
        If `True`, the step is only executed when needed by other steps.
    resources
        Named resources required to run this step, e.g. `{"gpu": 1}`.
        See `stepup.core.api.step()` for details.
    duration
        An initial estimate of the step's wall time in seconds.
        See `stepup.core.api.step()` for details.

    Returns
    -------
    step_info
        Holds relevant information of the step, useful for defining follow-up steps.
    """
    with subs_env_vars() as subs:
        path_html = subs(path_html)
        dest = subs(dest)
        step_info = subs(step_info)
    if not path_html.endswith(".html"):
        raise ValueError("The HTML file must have extension .html")
    path_pdf = make_path_out(path_html, dest, ".pdf")
    parts = ["sr-convert-weasyprint", shq(path_html), shq(path_pdf)]
    paths_out = [path_pdf]
    if weasyprint is not None:
        parts.append(f"--weasyprint={shq(weasyprint)}")
    if step_info is not None:
        parts.append(f"--step-info={shq(step_info)}")
        paths_out.append(step_info)
    return run(
        " ".join(parts),
        inp=path_html,
        out=paths_out,
        optional=optional,
        resources=resources,
        duration=duration,
    )


def diff_latex(
    path_old: StrPath,
    path_new: StrPath,
    dest: StrPath,
    *,
    latexdiff: StrPath | None = None,
    latexdiff_args: Collection[str] | None = None,
    optional: bool = False,
    resources: dict[str, int] | str | None = None,
    duration: float | None = None,
) -> StepInfo:
    r"""Create a step to run latexdiff.

    Parameters
    ----------
    path_old
        The old tex or bbl source.
    path_new
        The new tex or bbl source.
    dest
        The diff output tex or bbl, or a directory with a trailing slash.
        In a directory, the output has the same name as `path_new`.
        A file must have the same extension as `path_new`.
    latexdiff
        Path of the latexdiff  executable.
        Defaults to `${STEPUP_REPORT_LATEXDIFF}` variable or `latexdiff` if the variable is unset.
    latexdiff_args
        Additional arguments for latexdiff.
        Defaults to the value of `${STEPUP_REPORT_LATEXDIFF_ARGS}`, split like a shell command.
        If this variable is unset, the following default is used:

        ```
        --append-context2cmd=abstract,supplementary,dataavailability,funding, \
                             authorcontributions,conflictsofinterest,abbreviations
        ```

        The option `--no-label` is always added because it is needed to make the file reproducible.
    optional
        If `True`, the step is only executed when needed by other steps.
    resources
        Named resources required to run this step, e.g. `{"gpu": 1}`.
        See `stepup.core.api.step()` for details.
    duration
        An initial estimate of the step's wall time in seconds.
        See `stepup.core.api.step()` for details.

    Returns
    -------
    step_info
        Holds relevant information of the step, useful for defining follow-up steps.
    """
    path_diff = make_path_out(path_new, dest, None)
    if path_diff.suffix != Path(path_new).suffix:
        raise ValueError(f"The output of diff_latex must have the extension of {path_new}.")
    if latexdiff is None:
        latexdiff = getenv("STEPUP_REPORT_LATEXDIFF", "latexdiff")

    if latexdiff_args is None:
        value = getenv("STEPUP_REPORT_LATEXDIFF_ARGS")
        latexdiff_args = DEFAULT_LATEXDIFF_ARGS if value is None else shlex.split(value)

    parts = [shq(latexdiff)]
    parts.extend(shlex.quote(latexdiff_arg) for latexdiff_arg in latexdiff_args)
    parts.extend([shq([path_old, path_new]), "--no-label", ">", shq(path_diff)])
    return run(
        " ".join(parts),
        inp=[path_old, path_new],
        out=path_diff,
        shell=True,
        optional=optional,
        resources=resources,
        duration=duration,
    )


def flatten_latex(
    path_tex: StrPath,
    dest: StrPath | None = None,
    *,
    optional: bool = False,
    resources: dict[str, int] | str | None = None,
    duration: float | None = None,
) -> StepInfo:
    r"""Flatten structured LaTeX source files (substitute `\input` and friends by their content).

    Parameters
    ----------
    path_tex
        The main tex file to be converted.
    dest
        Output destination: `None`, a directory or a file.
        When `None`, the output is `{stem}-flat.tex` in the directory of `path_tex`.
        In a directory, the output has the same name as `path_tex`.
    optional
        If `True`, the step is only executed when needed by other steps.
    resources
        Named resources required to run this step, e.g. `{"gpu": 1}`.
        See `stepup.core.api.step()` for details.
    duration
        An initial estimate of the step's wall time in seconds.
        See `stepup.core.api.step()` for details.

    Returns
    -------
    step_info
        Holds relevant information of the step, useful for defining follow-up steps.
    """
    if not coerce_str(path_tex).endswith(".tex"):
        raise ValueError(f"The LaTeX source must have extension .tex, got {path_tex}.")
    if dest is None:
        path_flat = Path(f"{coerce_str(path_tex)[:-4]}-flat.tex")
    else:
        path_flat = make_path_out(path_tex, dest, ".tex")
    return run(
        f"sr-flatten-latex {shq(path_tex)} {shq(path_flat)}",
        inp=path_tex,
        out=path_flat,
        optional=optional,
        resources=resources,
        duration=duration,
    )


def nup_pdf(
    path_pdf: StrPath,
    dest: StrPath,
    *,
    nrow: int | None = None,
    ncol: int | None = None,
    margin: float | None = None,
    page_format: str | None = None,
    optional: bool = False,
    resources: dict[str, int] | str | None = None,
    duration: float | None = None,
) -> StepInfo:
    """Put multiple pages per sheet using a fixed layout.

    Parameters
    ----------
    path_pdf
        The original PDF document (with normal pages).
    dest
        The output PDF (with multiple pages per sheet), or a directory with a trailing slash.
        In a directory, the output has the same name as `path_pdf`.
    nrow
        The number of rows on each output sheet.
        The default is `${STEPUP_REPORT_NUP_NROW}` or 2 if the variable is not set.
    ncol
        The number of columns on each output sheet.
        The default is `${STEPUP_REPORT_NUP_NCOL}` or 2 if the variable is not set.
    margin
        The margin in mm between the pages on each sheet. (Also used as sheet margin.)
        The default is `${STEPUP_REPORT_NUP_MARGIN}` or 10.0 if the variable is not set.
    page_format
        The output page format.
        The default is `${STEPUP_REPORT_NUP_PAGE_FORMAT}` or A4-L if the variable is not set.
    optional
        If `True`, the step is only executed when needed by other steps.
    resources
        Named resources required to run this step, e.g. `{"gpu": 1}`.
        See `stepup.core.api.step()` for details.
    duration
        An initial estimate of the step's wall time in seconds.
        See `stepup.core.api.step()` for details.

    Returns
    -------
    step_info
        Holds relevant information of the step, useful for defining follow-up steps.
    """
    path_out = make_path_out(path_pdf, dest, ".pdf")
    parts = ["sr-nup-pdf", shq(path_pdf), shq(path_out)]
    if nrow is not None:
        parts.append(f"-r {nrow!s}")
    if ncol is not None:
        parts.append(f"-c {ncol!s}")
    if margin is not None:
        parts.append(f"-m {margin!s}")
    if page_format is not None:
        parts.append(f"-p {shlex.quote(page_format)}")
    return run(
        " ".join(parts),
        inp=path_pdf,
        out=path_out,
        optional=optional,
        resources=resources,
        duration=duration,
    )


def raster_pdf(
    path_pdf: StrPath,
    dest: StrPath,
    *,
    resolution: int | None = None,
    quality: int | None = None,
    optional: bool = False,
    resources: dict[str, int] | str | None = None,
    duration: float | None = None,
) -> StepInfo:
    """Render the pages of a PDF into a new PDF with JPEG bitmaps, or into PNG files.

    Parameters
    ----------
    path_pdf
        The input PDF file.
    dest
        A directory with a trailing slash or a file.
        In a directory, the output is a PDF with the same name as `path_pdf`.
        The output is a PDF file, unless `dest` is a file with extension `.png`.
        A PNG file is written for every page,
        and its name may contain the placeholders `{p}` (the page number),
        `{0p}` (the page number padded with zeros) and `{t}` (the number of pages),
        as in the output of `compile_typst()`.
        One of `{p}` and `{0p}` is required when the PDF has more than one page.
        With placeholders, the names of the PNG files are only known when the step runs,
        so they are amended as outputs of the step.
    resolution
        The resolution of the bitmap in dots per inch (dpi).
        The default value is taken from `${STEPUP_REPORT_RASTER_RESOLUTION}`
        or 100 if the variable is not set.
    quality
        The JPEG quality of the bitmap, only for PDF output.
        The default value is taken from `${STEPUP_REPORT_RASTER_QUALITY}`
        or 50 if the variable is not set.
    optional
        If `True`, the step is only executed when needed by other steps.
    resources
        Named resources required to run this step, e.g. `{"gpu": 1}`.
        See `stepup.core.api.step()` for details.
    duration
        An initial estimate of the step's wall time in seconds.
        See `stepup.core.api.step()` for details.

    Returns
    -------
    step_info
        Holds relevant information of the step, useful for defining follow-up steps.
    """
    path_out = make_path_out(path_pdf, dest, ".pdf", [".png"])
    if path_out.suffix == ".png" and quality is not None:
        raise ValueError("The JPEG quality cannot be used with PNG output.")
    parts = ["sr-raster-pdf", shq(path_pdf), shq(path_out)]
    if resolution is not None:
        parts.append(f"-r {resolution!s}")
    if quality is not None:
        parts.append(f"-q {quality!s}")
    has_placeholder = any(p in path_out for p in ("{p}", "{0p}", "{t}"))
    return run(
        " ".join(parts),
        inp=path_pdf,
        out=[] if has_placeholder else [path_out],
        optional=optional,
        resources=resources,
        duration=duration,
    )


def sanitize_bibtex(
    path_bib: StrPath,
    dest: StrPath | None = None,
    *,
    path_aux: StrPath | None = None,
    path_config: StrPath | None = None,
    optional: bool = False,
    resources: dict[str, int] | str | None = None,
    duration: float | None = None,
) -> StepInfo:
    """Sanitize a BibTeX file.

    Parameters
    ----------
    path_bib
        Path to the BibTeX file to be sanitized.
    dest
        If given, the cleaned-up BibTeX file is written to this file,
        or to a file with the same name in this directory, when it has a trailing slash.
        You can manually copy it back to the original if you approve of the cleanup.
        If not given, the original BibTeX file is overwritten when it needs a cleanup,
        which will drain the scheduler.
        You then check if the updated version is correct and rerun the build to approve.
    path_aux
        Path to the LaTeX aux file, if any.
        This is used to detect unused or missing citations.
    path_config
        The YAML configuration file for the `sr-bibsane` script.
    optional
        If `True`, the step is only executed when needed by other steps.
    resources
        Named resources required to run this step, e.g. `{"gpu": 1}`.
        See `stepup.core.api.step()` for details.
    duration
        An initial estimate of the step's wall time in seconds.
        See `stepup.core.api.step()` for details.

    Returns
    -------
    step_info
        Holds relevant information of the step, useful for defining follow-up steps.
    """
    with subs_env_vars() as subs:
        path_bib = subs(path_bib)
        path_config = subs(path_config)
        path_aux = subs(path_aux)
        dest = subs(dest)
    if not path_bib.endswith(".bib"):
        raise ValueError("The BibTeX file must have extension .bib")

    parts = ["sr-bibsane", shq(path_bib)]
    paths_inp = [path_bib]
    if path_aux is not None:
        parts.append(f"--aux={shq(path_aux)}")
        paths_inp.append(path_aux)
    if path_config is not None:
        parts.append(f"--config={shq(path_config)}")
        paths_inp.append(path_config)
    paths_out = []
    if dest is not None:
        path_out = make_path_out(path_bib, dest, ".bib")
        parts.append(f"--out={shq(path_out)}")
        paths_out.append(path_out)
    return run(
        " ".join(parts),
        inp=paths_inp,
        out=paths_out,
        optional=optional,
        resources=resources,
        duration=duration,
    )


def unplot(
    path_svg: StrPath,
    dest: StrPath | None = None,
    *,
    optional: bool = False,
    resources: dict[str, int] | str | None = None,
    duration: float | None = None,
) -> StepInfo:
    """Convert a plot back to data.

    Parameters
    ----------
    path_svg
        The SVG file with paths to be converted back.
    dest
        An output directory or file.
    optional
        If `True`, the step is only executed when needed by other steps.
    resources
        Named resources required to run this step, e.g. `{"gpu": 1}`.
        See `stepup.core.api.step()` for details.
    duration
        An initial estimate of the step's wall time in seconds.
        See `stepup.core.api.step()` for details.

    Returns
    -------
    step_info
        Holds relevant information of the step, useful for defining follow-up steps.
    """
    path_out = make_path_out(path_svg, dest, ".json")
    command = f"sr-unplot {shq(path_svg)} {shq(path_out)}"
    return run(
        command,
        inp=path_svg,
        out=path_out,
        optional=optional,
        resources=resources,
        duration=duration,
    )
