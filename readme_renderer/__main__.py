import argparse
from readme_renderer.markdown import render as render_md
from readme_renderer.rst import render as render_rst
from readme_renderer.txt import render as render_txt
import pathlib
from importlib.metadata import metadata
import sys
import pygments.formatters as f
from typing import Optional, List


def main(cli_args: Optional[List[str]] = None) -> None:
    parser = argparse.ArgumentParser(
        description="Renders a .md, .rst, or .txt README to HTML",
    )
    parser.add_argument("-p", "--package", help="Get README from package metadata",
                        action="store_true")
    parser.add_argument("-f", "--format", choices=["md", "rst", "txt"],
                        help="README format (inferred from input file name or package)")
    parser.add_argument('input', help="Input README file or package name")
    parser.add_argument('-o', '--output', help="Output file (default: stdout)",
                        type=argparse.FileType('w'), default='-')
    args = parser.parse_args(cli_args)

    content_format = args.format
    if args.package:
        message = metadata(args.input)
        source = message.get_payload()  # type: ignore[attr-defined] # noqa: E501 https://peps.python.org/pep-0566/

        # Infer the format of the description from package metadata.
        if not content_format:
            content_type = message.get("Description-Content-Type", "text/x-rst")
            if content_type == "text/x-rst":
                content_format = "rst"
            elif content_type == "text/markdown":
                content_format = "md"
            elif content_type == "text/plain":
                content_format = "txt"
            else:
                raise ValueError(f"invalid content type {content_type} for package "
                                 "`long_description`")
    else:
        filename = pathlib.Path(args.input)
        content_format = content_format or filename.suffix.lstrip(".")
        with filename.open() as fp:
            source = fp.read()

    if content_format == "md":
        rendered = render_md(source, stream=sys.stderr)
    elif content_format == "rst":
        rendered = render_rst(source, stream=sys.stderr)
    elif content_format == "txt":
        rendered = render_txt(source, stream=sys.stderr)
    else:
        raise ValueError(f"invalid README format: {content_format} (expected `md`, "
                         "`rst`, or `txt`)")
    if rendered is None:
        sys.exit(1)

    pygment_styles = '\n'.join(
        filter(lambda e: r'pre {' not in e.strip(),
               f.HtmlFormatter().get_style_defs().split('\n'))
    )
    rendered = f"""<!DOCTYPE html>
    <html xmlns="http://www.w3.org/1999/xhtml" lang="es" xml:lang="es">
    <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=yes" />
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/github-markdown-css/5.5.1/github-markdown-light.css" integrity="sha512-twSIkcOWTg8pO2szOkSwXeumnI79JQ0zVRavBB5cdJvhVFhReF9fBlyFM380P6vKIQ4mlD80EPtuZdSPpqYDgQ==" crossorigin="anonymous" referrerpolicy="no-referrer" />
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.9/katex.css" integrity="sha512-8Sjzsdvg/n5bk1R2UoBRNzowylImkCddXj0QXeHSDIW0Ad8mebfIkGxUSfrPzEt7km4MqRMMT3RSF4gGxTVqGw==" crossorigin="anonymous" referrerpolicy="no-referrer" />
        <style>
            .markdown-body {{
                box-sizing: border-box;
                min-width: 200px;
                max-width: 980px;
                margin: 0 auto;
                padding: 45px;
            }}
            .markdown-body table {{
                max-width: fit-content;
            }}
            .markdown-body h1:is(:nth-of-type(n+4)) {{
                page-break-before: always;
            }}
            .markdown-body pre {{
                line-height: 1em;
                break-inside: avoid;
                {pygment_styles}
            }}
            .markdown-body li {{
                break-inside: avoid;
            }}
            @media (max-width: 767px) {{
                .markdown-body {{
                    padding: 15px;
                }}
            }}
        </style>
    </head>
    <body>
        <article class="markdown-body">
            {rendered}
        </article>
    </body>
    </html>"""

    print(rendered, file=args.output)


if __name__ == '__main__':
    main()
