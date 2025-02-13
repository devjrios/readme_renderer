# Copyright 2015 Donald Stufft
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import Any, Optional

from readme_renderer.math_parser import MathParser, MathSymbolParser

from .clean import clean

from html import escape as html_escape


def render(raw: str, **kwargs: Any) -> Optional[str]:
    rendered = html_escape(raw).replace("\n", "<br>")
    fenced_doc = MathSymbolParser(raw_document=rendered).render
    math_rendered = MathParser(html=fenced_doc).render
    return clean(math_rendered,
                 tags={"br", "path", "svg", "span"},
                 attributes={
                    "span": {"class", "style", "aria-hidden"},
                    "path": {"d"},
                    "svg": {"xmlns", "width", "height", "viewBox",
                            "preserveAspectRatio"},
                 })
