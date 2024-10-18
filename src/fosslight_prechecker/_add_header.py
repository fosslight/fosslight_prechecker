#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2021 LG Electronics Inc.
# SPDX-FileCopyrightText: 2019 Free Software Foundation Europe e.V. <https://fsfe.org>
# SPDX-FileCopyrightText: 2019 Stefan Bakker <s.bakker777@gmail.com>
# SPDX-FileCopyrightText: 2019 Kirill Elagin <kirelagin@gmail.com>
# SPDX-FileCopyrightText: 2020 Dmitry Bogatov
# SPDX-FileCopyrightText: © 2020 Liferay, Inc. <https://liferay.com>
# SPDX-FileCopyrightText: 2021 Alvar Penning
# SPDX-FileCopyrightText: 2021 Alliander N.V. <https://alliander.com>
# SPDX-FileCopyrightText: 2021 Robin Vobruba <hoijui.quaero@gmail.com>
# SPDX-FileCopyrightText: 2022 Florian Snow <florian@familysnow.net>
# SPDX-License-Identifier: GPL-3.0-only

import logging
import datetime
import argparse
import sys
import re
import fosslight_util.constant as constant
from os import PathLike
from gettext import gettext as _
from pathlib import Path
from typing import NamedTuple, Optional, Set

from jinja2 import Environment, FileSystemLoader, PackageLoader, Template, select_autoescape
from boolean.boolean import ParseError, Expression
from license_expression import ExpressionError

from reuse.lint import (
    add_arguments as lint_add_arguments,
    run as lint_run
)
from reuse._util import (
    PathType,
    _COPYRIGHT_STYLES,
    _COPYRIGHT_PATTERNS,
    _END_PATTERN,
    _LICENSING,
    filter_ignore_block,
    find_license_identifiers,
    contains_spdx_info,
    detect_line_endings,
    _determine_license_path,
    make_copyright_line,
    merge_copyright_lines,
    spdx_identifier
)
from reuse._comment import (
    NAME_STYLE_MAP,
    CCommentStyle,
    CommentCreateError,
    CommentStyle,
    EmptyCommentStyle,
    HtmlCommentStyle,
    PythonCommentStyle
)
from reuse.header import (
    MissingSpdxInfo,
    _get_comment_style,
    _verify_write_access,
    _verify_paths_line_handling,
    _verify_paths_comment_style,
    _is_uncommentable,
    _determine_license_suffix_path,
    _find_first_spdx_comment,
    _extract_shebang,
)
from reuse.download import (
    add_arguments as download_add_arguments,
    run as reuse_download
)
from reuse._format import fill_all
from reuse.project import Project


logger = logging.getLogger(constant.LOGGER_NAME)

#: Simple structure for holding SPDX information.
#:
#: The two iterables MUST be sets.
SpdxInfo = NamedTuple(
    "SpdxInfo",
    [("spdx_expressions", Set[Expression]), ("copyright_lines", Set[str]), ("dl_url", Set[str])]
)

_DL_URL_PATTERNS = [
    re.compile(r"(?P<dl_url>SPDX-PackageDownloadLocation:[ \t]+(.*?))" + _END_PATTERN)
]

_DL_URL_STYLES = {
    "spdx": "SPDX-PackageDownloadLocation:",
    "string": "PackageDownloadLocation",
}


def get_loader():
    if getattr(sys, 'frozen', False):
        dft_dir = sys._MEIPASS
        loader = FileSystemLoader(str(dft_dir))
    else:
        loader = PackageLoader("fosslight_prechecker", "templates")
    return loader


_ENV = Environment(loader=get_loader(), autoescape=select_autoescape([]), trim_blocks=True)
DEFAULT_TEMPLATE = _ENV.get_template("default_template.jinja2")


def extract_spdx_info(text: str) -> SpdxInfo:
    """Extract SPDX information from comments in a string.

    :raises ExpressionError: if an SPDX expression could not be parsed
    :raises ParseError: if an SPDX expression could not be parsed
    """
    text = filter_ignore_block(text)
    expression_matches = set(find_license_identifiers(text))
    expressions = set()
    copyright_matches = set()
    dl_url = set()
    for expression in expression_matches:
        try:
            expressions.add(_LICENSING.parse(expression))
        except (ExpressionError, ParseError):
            logger.error(
                _("Could not parse '{expression}'").format(
                    expression=expression
                )
            )
            raise
    for line in text.splitlines():
        for pattern in _COPYRIGHT_PATTERNS:
            match = pattern.search(line)
            if match is not None:
                copyright_matches.add(match.groupdict()["copyright"].strip())
                break
        for pattern in _DL_URL_PATTERNS:
            match = pattern.search(line)
            if match is not None:
                dl_url.add(match.groupdict()["dl_url"].strip())
                break

    return SpdxInfo(expressions, copyright_matches, dl_url)


def _create_new_header(
    spdx_info: SpdxInfo,
    template: Template = None,
    template_is_commented: bool = False,
    style: CommentStyle = None,
    force_multi: bool = False,
) -> str:
    """Format a new header from scratch.

    :raises CommentCreateError: if a comment could not be created.
    :raises MissingSpdxInfo: if the generated comment is missing SPDX
        information.
    """
    if template is None:
        template = DEFAULT_TEMPLATE
        logger.warning(f"Using default template: {template}")
    if style is None:
        style = PythonCommentStyle

    try:
        rendered = template.render(
            copyright_lines=sorted(spdx_info.copyright_lines),
            spdx_expressions=sorted(map(str, spdx_info.spdx_expressions)),
            dl_url=sorted(spdx_info.dl_url),
        ).strip("\n")
    except Exception as ex:
        logger.info(f"Error to create new header: {ex}")

    if template_is_commented:
        result = rendered
    else:
        result = style.create_comment(rendered, force_multi=force_multi).strip("\n")

    # Verify that the result contains all SpdxInfo.
    new_spdx_info = extract_spdx_info(result)
    if (
        spdx_info.copyright_lines != new_spdx_info.copyright_lines
        and spdx_info.spdx_expressions != new_spdx_info.spdx_expressions
        and spdx_info.dl_url != new_spdx_info.dl_url
    ):
        logger.debug(
            _(
                "generated comment is missing copyright lines or license"
                " expressions"
            )
        )
        logger.debug(result)
        raise MissingSpdxInfo()

    return result


def create_header(
    spdx_info: SpdxInfo,
    header: str = None,
    template: Template = None,
    template_is_commented: bool = False,
    style: CommentStyle = None,
    force_multi: bool = False,
    merge_copyrights: bool = False,
) -> str:
    """Create a header containing *spdx_info*. *header* is an optional argument
    containing a header which should be modified to include *spdx_info*. If
    *header* is not given, a brand new header is created.

    *template*, *template_is_commented*, and *style* determine what the header
    will look like, and whether it will be commented or not.

    :raises CommentCreateError: if a comment could not be created.
    :raises MissingSpdxInfo: if the generated comment is missing SPDX
        information.
    """
    if template is None:
        template = DEFAULT_TEMPLATE
    if style is None:
        style = PythonCommentStyle

    new_header = ""
    if header:
        try:
            existing_spdx = extract_spdx_info(header)
        except (ExpressionError, ParseError) as err:
            raise CommentCreateError(
                "existing header contains an erroneous SPDX expression"
            ) from err

        if merge_copyrights:
            spdx_copyrights = merge_copyright_lines(
                spdx_info.copyright_lines.union(existing_spdx.copyright_lines),
            )
        else:
            spdx_copyrights = spdx_info.copyright_lines.union(
                existing_spdx.copyright_lines
            )

        # TODO: This behaviour does not match the docstring.
        spdx_info = SpdxInfo(
            spdx_info.spdx_expressions.union(existing_spdx.spdx_expressions),
            spdx_copyrights,
            spdx_info.dl_url.union(existing_spdx.dl_url),
        )

    new_header += _create_new_header(
        spdx_info,
        template=template,
        template_is_commented=template_is_commented,
        style=style,
        force_multi=force_multi,
    )
    return new_header


def find_and_replace_header(
    text: str,
    spdx_info: SpdxInfo,
    template: Template = None,
    template_is_commented: bool = False,
    style: CommentStyle = None,
    force_multi: bool = False,
) -> str:
    """Find the first SPDX comment block in *text*. That comment block is
    replaced by a new comment block containing *spdx_info*. It is formatted as
    according to *template*. The template is normally uncommented, but if it is
    already commented, *template_is_commented* should be :const:`True`.

    If both *style* and *template_is_commented* are provided, *style* is only
    used to find the header comment.

    If the comment block already contained some SPDX information, that
    information is merged into *spdx_info*.

    If no header exists, one is simply created.

    *text* is returned with a new header.

    :raises CommentCreateError: if a comment could not be created.
    :raises MissingSpdxInfo: if the generated comment is missing SPDX
        information.
    """
    if style is None:
        style = PythonCommentStyle

    try:
        before, header, after = _find_first_spdx_comment(text, style=style)
    except MissingSpdxInfo:
        before, header, after = "", "", text

    # Workaround. EmptyCommentStyle should always be completely replaced.
    if style is EmptyCommentStyle:
        after = ""

    logger.debug(f"before = {repr(before)}")
    logger.debug(f"header = {repr(header)}")
    logger.debug(f"after = {repr(after)}")

    # Keep special first-line-of-file lines as the first line in the file,
    # or say, move our comments after it.
    for prefix in (
        prefix
        for com_style, prefix in (
            (CCommentStyle, "#!"),  # e.g. V-Lang
            (HtmlCommentStyle, "<?xml"),  # e.g. XML/XHTML
            (PythonCommentStyle, "#!"),  # e.g. Shell, Python
        )
        if style is com_style
    ):
        # Extract shebang from header and put it in before. It's a bit messy,
        # but it ends up working.
        if header.startswith(prefix) and not before.strip():
            before, header = _extract_shebang(prefix, header)
        elif after.startswith(prefix) and not any((before, header)):
            before, after = _extract_shebang(prefix, after)

    header = create_header(
        spdx_info,
        header,
        template=template,
        template_is_commented=template_is_commented,
        style=style,
        force_multi=force_multi,
    )

    new_text = f"{header}\n"
    if before.strip():
        new_text = f"{before.rstrip()}\n\n{new_text}"
    if after.strip():
        new_text = f"{new_text}\n{after.lstrip()}"
    return new_text


def _add_header_to_file(
    path: PathLike,
    spdx_info: SpdxInfo,
    template: Template,
    template_is_commented: bool,
    style: Optional[str],
    force_multi: bool = False,
    skip_existing: bool = False,
    out=sys.stdout,
) -> int:
    """Helper function."""
    # pylint: disable=too-many-arguments
    result = 0
    if style is not None:
        style = NAME_STYLE_MAP[style]
    else:
        style = _get_comment_style(path)
        if style is None:
            out.write(_("Skipped unrecognised file {path}").format(path=path))
            out.write("\n")
            return result

    with path.open("r", encoding="utf-8", newline="") as fp:
        text = fp.read()

    # Ideally, this check is done elsewhere. But that would necessitate reading
    # the file contents before this function is called.
    if skip_existing and contains_spdx_info(text):
        out.write(
            _(
                "Skipped file '{path}' already containing SPDX information"
            ).format(path=path)
        )
        out.write("\n")
        return result

    # Detect and remember line endings for later conversion.
    line_ending = detect_line_endings(text)
    # Normalise line endings.
    text = text.replace(line_ending, "\n")

    try:
        output = find_and_replace_header(
            text,
            spdx_info,
            template=template,
            template_is_commented=template_is_commented,
            style=style,
            force_multi=force_multi,
        )

    except CommentCreateError:
        out.write(
            _("Error: Could not create comment for '{path}'").format(path=path)
        )
        out.write("\n")
        result = 1
    except MissingSpdxInfo:
        out.write(
            _(
                "Error: Generated comment header for '{path}' is missing"
                " copyright lines or license expressions. The template is"
                " probably incorrect. Did not write new header."
            ).format(path=path)
        )
        out.write("\n")
        result = 1
    else:
        with path.open("w", encoding="utf-8", newline=line_ending) as fp:
            fp.write(output)
        # TODO: This may need to be rephrased more elegantly.
        out.write(_("Successfully changed header of {path}").format(path=path))
        out.write("\n")

    return result


def add_command(
    subparsers,
    name: str,
    add_arguments_func,
    run_func,
    formatter_class=None,
    description: str = None,
    help: str = None,
    aliases: list = None,
) -> None:
    """Add a subparser for a command."""
    if formatter_class is None:
        formatter_class = argparse.RawTextHelpFormatter
    subparser = subparsers.add_parser(
        name,
        formatter_class=formatter_class,
        description=description,
        help=help,
        aliases=aliases or [],
    )
    add_arguments_func(subparser)
    subparser.set_defaults(func=run_func)
    subparser.set_defaults(parser=subparser)


def header_add_arguments(parser) -> None:
    """Add arguments to parser."""
    parser.add_argument(
        "--copyright",
        "-c",
        action="append",
        type=str,
        help=_("copyright statement, repeatable"),
    )
    parser.add_argument(
        "--license",
        "-l",
        action="append",
        type=spdx_identifier,
        help=_("SPDX Identifier, repeatable"),
    )
    parser.add_argument(
        "--dlurl",
        "-u",
        action="append",
        type=str,
        help=_("download location statement, repeatable"),
    )
    parser.add_argument(
        "--year",
        "-y",
        action="append",
        type=str,
        help=_("year of copyright statement, optional"),
    )
    parser.add_argument(
        "--style",
        "-s",
        action="store",
        type=str,
        choices=list(NAME_STYLE_MAP),
        help=_("comment style to use, optional"),
    )
    parser.add_argument(
        "--copyright-style",
        action="store",
        choices=list(_COPYRIGHT_STYLES.keys()),
        help=_("copyright style to use, optional"),
    )
    parser.add_argument(
        "--template",
        "-t",
        action="store",
        type=str,
        help=_("name of template to use, optional"),
    )
    parser.add_argument(
        "--exclude-year",
        action="store_true",
        help=_("do not include year in statement"),
    )
    parser.add_argument(
        "--merge-copyrights",
        action="store_true",
        help=_("merge copyright lines if copyright statements are identical"),
    )
    parser.add_argument(
        "--single-line",
        action="store_true",
        help=_("force single-line comment style, optional"),
    )
    parser.add_argument(
        "--multi-line",
        action="store_true",
        help=_("force multi-line comment style, optional"),
    )
    parser.add_argument(
        "--explicit-license",
        action="store_true",
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--force-dot-license",
        action="store_true",
        help=_("write a .license file instead of a header inside the file"),
    )
    parser.add_argument(
        "--recursive",
        "-r",
        action="store_true",
        help=_(
            "add headers to all files under specified directories recursively"
        ),
    )
    parser.add_argument(
        "--no-replace",
        action="store_true",
        help=_(
            "do not replace the first header in the file; just add a new one"
        ),
    )
    parser.add_argument(
        "--skip-unrecognised",
        action="store_true",
        help=_("skip files with unrecognised comment styles"),
    )
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        help=_("skip files that already contain SPDX information"),
    )
    parser.add_argument("path", action="store", nargs="+", type=PathType("r"))


def reuse_parser() -> argparse.ArgumentParser:
    """Create the parser and return it."""
    # pylint: disable=redefined-outer-name
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument(
        "--debug", action="store_true", help=_("enable debug statements")
    )
    parser.add_argument(
        "--include-submodules",
        action="store_true",
        help=_("do not skip over Git submodules"),
    )
    parser.add_argument(
        "--no-multiprocessing",
        action="store_true",
        help=_("do not use multiprocessing"),
    )
    parser.add_argument(
        "--root",
        action="store",
        metavar="PATH",
        type=PathType("r", force_directory=True),
        help=_("define root of project"),
    )
    parser.add_argument(
        "--version",
        action="store_true",
        help=_("show program's version number and exit"),
    )
    parser.set_defaults(func=lambda *args: parser.print_help())

    subparsers = parser.add_subparsers(title=_("subcommands"))

    add_command(
        subparsers,
        "addheader",
        header_add_arguments,
        add_header,
        help=_("add copyright and licensing into the header of files"),
        description=fill_all(
            _(
                "Add copyright and licensing into the header of one or more"
                " files.\n"
                "\n"
                "By using --copyright and --license, you can specify which"
                " copyright holders and licenses to add to the headers of the"
                " given files.\n"
                "\n"
                "The comment style should be auto-detected for your files. If"
                " a comment style could not be detected and --skip-unrecognised"
                " is not specified, the process aborts. Use --style to specify"
                " or override the comment style to use.\n"
                "\n"
                "A single-line comment style is used when it is available. If"
                " no single-line comment style is available, a multi-line"
                " comment style is used. You can force a certain comment style"
                " using --single-line or --multi-line.\n"
                "\n"
                "You can change the template of the header comment by using"
                " --template. Place a Jinja2 template in"
                " .reuse/templates/mytemplate.jinja2. You can use the template"
                " by specifying"
                " '--template mytemplate'. Read the online documentation on"
                " how to use this feature.\n"
                "\n"
                "If a binary file is detected, or if --explicit-license is"
                " specified, the header is placed in a .license file.\n"
                # TODO: Remove this
                "\n"
                "IMPORTANT: This is currently EXPERIMENTAL!"
            )
        ),
    )

    add_command(
        subparsers,
        "lint",
        lint_add_arguments,
        lint_run,
        help=_("list all non-compliant files"),
        description=fill_all(
            _(
                "Lint the project directory for compliance with"
                " the REUSE Specification. You can"
                " find the latest version of the specification at"
                " <https://reuse.software/spec/>.\n"
                "\n"
                "Specifically, the following criteria are checked:\n"
                "\n"
                "- Are there any bad (unrecognised, not compliant with SPDX)"
                " licenses in the project?\n"
                "\n"
                "- Are any licenses referred to inside of the project, but"
                " not included in the LICENSES/ directory?\n"
                "\n"
                "- Are any licenses included in the LICENSES/ directory that"
                " are not used inside of the project?\n"
                "\n"
                "- Do all files have valid copyright and licensing"
                " information?"
            )
        ),
    )

    add_command(
        subparsers,
        "download",
        download_add_arguments,
        reuse_download,
        help=_("download a license and place it in the LICENSES/ directory"),
        description=fill_all(
            _(
                "Download a license and place it in the LICENSES/ directory.\n"
                "\n"
                "The LICENSES/ directory is automatically found in the"
                " following order:\n"
                "\n"
                "- The LICENSES/ directory in the root of the VCS"
                " repository.\n"
                "\n"
                "- The current directory if its name is LICENSES.\n"
                "\n"
                "- The LICENSES/ directory in the current directory.\n"
                "\n"
                "If the LICENSES/ directory cannot be found, one is simply"
                " created."
            )
        ),
    )
    return parser


def make_dl_url_line(statement: str, dl_url_style: str = "spdx") -> str:
    """Given a statement, prefix it with ``SPDX-PackageDownloadLocation:`` if it is
    not already prefixed with some manner of copyright tag.
    """
    if "\n" in statement:
        raise RuntimeError(f"Unexpected newline in '{statement}'")

    dl_url_prefix = _DL_URL_STYLES.get(dl_url_style)
    if dl_url_prefix is None:
        raise RuntimeError("Unexpected dl_url_prefix style: Need 'spdx', 'string'")

    for pattern in _DL_URL_PATTERNS:
        try:
            match = pattern.search(statement)
        except Exception as ex:
            logger.info(f"Error to search url pattern : {ex}")
        if match is not None:
            return statement
    return f"{dl_url_prefix} {statement}"


def add_header(args, project: Project, out=sys.stdout) -> int:
    """Add headers to files."""
    # pylint: disable=too-many-branches
    if not any((args.copyright, args.license, args.dlurl)):
        args.parser.error(_("option --copyright or --license is required"))

    if args.exclude_year and args.year:
        args.parser.error(
            _("option --exclude-year and --year are mutually exclusive")
        )

    if args.single_line and args.multi_line:
        args.parser.error(
            _("option --single-line and --multi-line are mutually exclusive")
        )

    if args.style is not None and args.skip_unrecognised:
        logger.warning(
            _(
                "--skip-unrecognised has no effect when used together with"
                " --style"
            )
        )

    if args.explicit_license:
        logger.warning(
            _(
                "--explicit-license has been deprecated in favour of"
                " --force-dot-license"
            )
        )
        args.force_dot_license = True

    paths = [_determine_license_path(path) for path in args.path]

    if not args.force_dot_license:
        _verify_write_access(paths, args.parser)

    # Verify line handling and comment styles before proceeding
    if args.style is None and not args.force_dot_license:
        _verify_paths_line_handling(
            paths,
            args.parser,
            force_single=args.single_line,
            force_multi=args.multi_line,
        )
        if not args.skip_unrecognised:
            _verify_paths_comment_style(paths, args.parser)

    template = None
    commented = False

    year = None
    if not args.exclude_year:
        if args.year:
            year = args.year
        else:
            year = datetime.date.today().year

    expressions = set(args.license) if args.license is not None else set()
    copyright_style = (
        args.copyright_style if args.copyright_style is not None else "spdx"
    )
    # same as copyright_style
    dl_url_style = (
        args.copyright_style if args.copyright_style is not None else "spdx"
    )
    copyright_lines = (
        {
            make_copyright_line(x, year=year, copyright_style=copyright_style)
            for x in args.copyright
        }
        if args.copyright is not None
        else set()
    )

    dl_url_lines = (
        {
            make_dl_url_line(url, dl_url_style=dl_url_style)
            for url in args.dlurl
        }
        if args.dlurl is not None
        else set()
    )
    spdx_info = SpdxInfo(expressions, copyright_lines, dl_url_lines)

    result = 0
    for path in paths:
        uncommentable = _is_uncommentable(path)
        if uncommentable or args.force_dot_license:
            new_path = _determine_license_suffix_path(path)
            if uncommentable:
                logger.info(
                    _(
                        "'{path}' is a binary, therefore using '{new_path}'"
                        " for the header"
                    ).format(path=path, new_path=new_path)
                )
            path = Path(new_path)
            path.touch()
        result += _add_header_to_file(
            path=path,
            spdx_info=spdx_info,
            template=template,
            template_is_commented=commented,
            style=args.style,
            force_multi=args.multi_line,
            skip_existing=args.skip_existing,
            out=out,
        )

    return min(result, 1)
