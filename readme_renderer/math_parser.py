"""
    Dataclasses for transforming TeX syntax to HTML.

    Uses the official JavaScript KaTeX CDN script, after minifying it with esbuild
    and removing the global export.

    The goal is to use the renderToString function inside that script that can
    convienently parse TeX expressions into HTML.

    Runs off the Chromium V8 engine using the official Cloudflare lib.
    CREDIT: https://github.com/cloudflare/stpyv8

    @author: jrios
    @date: 2024-02-03 'ISO-8601'
"""

import STPyV8
import re
from html import unescape
from typing import Any, List, Optional
from dataclasses import dataclass, field
from pathlib import Path
from functools import partial


@dataclass(kw_only=True)
class MathParser:
    __version__: str = field(init=False, default="0.16.9")
    html: str = field(default=...)
    # JS script containing function katex.renderToString
    script_src: Optional[str] = field(
        default=f"{Path(__file__).parent.resolve()}/bundle/katex.min.js",
        metadata={"version": __version__},
    )
    script_content: str = field(init=False, default=None)

    def __post_init__(self):
        if not self.script_src or not Path(self.script_src).resolve().is_file():
            raise ValueError("Math Script Path wasn't found.")
        with open(self.script_src, "r") as kt:
            self.script_content = kt.read()

    @property
    def render(self) -> Optional[str]:
        with STPyV8.JSContext() as context:
            context.eval(self.script_content)
            renderToString: STPyV8.JSFunction = context.eval("katex.renderToString")

            code_expr = re.compile(
                r'<pre lang="math"(?P<inline> inline|)>(.*?)<code>(?P<math>.+?)'
                r'</code>(.*?)</pre>'
                ,re.DOTALL)
            def replacer(html_fence: re.Match[Any]):
                math = html_fence.group("math")
                math = None if not math else math.strip()

                inline = html_fence.group("inline")
                inline = None if not inline else inline.strip()

                if not math:
                    return
                math = unescape(math)
                math = renderToString(math, {"throwOnError": False,
                                             "fleqn": False,
                                             "displayMode": not bool(inline),
                                             "output": "html"})
                if not inline:
                    return (r'<pre lang="math">'f"""{math}"""r'</pre>')
                return math
            return code_expr.sub(replacer, self.html)


@dataclass(kw_only=True)
class MathSymbolParser:
    """
        Replaces well known delimiters with standard fences,
        also adding an inline attribute when needed.

        The input should be the raw document before passing
        through the HTML converter.

        (GFM breaks latex syntax for some content,
        so we pre-fence things with <pre> and <code> tags so it can play nice)
    """
    delimiters: List[Any] = field(init=False, default=None)
    raw_document: str = field(default=...)

    def __post_init__(self):

        if not self.raw_document:
            raise ValueError("invalid README format: invalid")

        self.delimiters = [
            {"start": "$$", "end": "$$", "inline": False},
            {"start": "\\begin{equation}", "end": "\\end{equation}", "inline": False},
            {"start": "\\begin{align}", "end": "\\end{align}", "inline": False},
            {"start": "\\begin{alignat}", "end": "\\end{alignat}", "inline": False},
            {"start": "\\begin{gather}", "end": "\\end{gather}", "inline": False},
            {"start": "\\begin{CD}", "end": "\\end{CD}", "inline": False},
            {"start": "\\[", "end": "\\]", "inline": False},
            {"start": "\\(", "end": "\\)", "inline": True},
            {"start": "$`", "end": "`$", "inline": True},
            {"start": "$", "end": "$", "inline": True},
        ]
    
    @property
    def render(self) -> Optional[str]:
        doc: str = self.raw_document

        def replacer(inline: bool, tex_expr: re.Match[Any]):
            content: str = tex_expr.group("content")
            content = None if not content else content.strip()
            if not content:
                return
            return (f'<pre lang="math"{" inline" if inline else ""}>'
                    f"""<code>{content}</code>"""r'</pre>')

        for delimiter in filter(lambda e: not e['inline'], self.delimiters):
            pattern = (
                "(?<!```)"
                + re.escape(delimiter["start"]) + r'(?P<content>.*?)'
                + re.escape(delimiter["end"])
                + "(?!```)"
            )
            math_expr = re.compile(pattern, re.DOTALL)
            _replacer = partial(replacer, delimiter['inline'])
            doc = math_expr.sub(_replacer, doc)

        for delimiter in filter(lambda e: e['inline'], self.delimiters):
            pattern = (
                re.escape(delimiter["start"]) + r'(?P<content>.*?)'
                + re.escape(delimiter["end"])
            )
            math_expr = re.compile(pattern, re.DOTALL)
            _replacer = partial(replacer, delimiter['inline'])

            for expr in self.find_non_fenced_lines(doc):
                sub = math_expr.sub(_replacer, expr)
                if sub and sub.strip():
                    doc = doc.replace(expr, sub)
        
        return doc

    def find_non_fenced_lines(self, text: str):
        code_pattern = re.compile(r'(<pre>|<code>|```.+?).*?(</pre>|</code>|```)', re.DOTALL)
        input_without_occurrences = code_pattern.sub('', text)
        lines = input_without_occurrences.split('\n')
        return [line for line in lines if line.strip()]
