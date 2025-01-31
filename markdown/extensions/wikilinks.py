# WikiLinks Extension for Python-Markdown
# ======================================

# Converts [[WikiLinks]] to relative links.

# See https://Python-Markdown.github.io/extensions/wikilinks
# for documentation.

# Original code Copyright [Waylan Limberg](http://achinghead.com/).

# All changes Copyright The Python Markdown Project

# License: [BSD](https://opensource.org/licenses/bsd-license.php)

"""
Converts `[[WikiLinks]]` to relative links.

See the [documentation](https://Python-Markdown.github.io/extensions/wikilinks)
for details.
"""

from __future__ import annotations

from . import Extension
from ..inlinepatterns import InlineProcessor
import xml.etree.ElementTree as etree
import re
from typing import Any


def build_url(label: str, base: str, end: str) -> str:
    """ Build a URL from the label, a base, and an end. """
    clean_label = re.sub(r'([ ]+_)|(_[ ]+)|([ ]+)', '_', label)
    return '{}{}{}'.format(base, clean_label, end)


class WikiLinkExtension(Extension):
    """ Add inline processor to Markdown. """

    def __init__(self, **kwargs):
        self.config = {
            'base_url': ['/', 'String to append to beginning or URL.'],
            'end_url': ['/', 'String to append to end of URL.'],
            'html_class': ['wikilink', 'CSS hook. Leave blank for none.'],
            'build_url': [build_url, 'Callable formats URL from label.'],
        }
        """ Default configuration options. """
        super().__init__(**kwargs)

    def extendMarkdown(self, md):
        self.md = md

        # append to end of inline patterns
        WIKILINK_RE = r'\[\[([\w0-9_ -]+)\]\]'
        wikilinkPattern = WikiLinksInlineProcessor(WIKILINK_RE, self.getConfigs())
        wikilinkPattern.md = md
        md.inlinePatterns.register(wikilinkPattern, 'wikilink', 75)


class WikiLinksInlineProcessor(InlineProcessor):
    """ Build link from `wikilink`. """

    def __init__(self, pattern: str, config: dict[str, Any]):
        super().__init__(pattern)
        self.config = config

    def handleMatch(self, m: re.Match[str], data: str) -> tuple[etree.Element | str, int, int]:
        if m.group(1).strip():
            base_url, end_url, html_class = self._getMeta()
            label = m.group(1).strip()
            url = self.config['build_url'](label, base_url, end_url)
            a = etree.Element('a')
            a.text = label
            a.set('href', url)
            if html_class:
                a.set('class', html_class)
        else:
            a = ''
        return a, m.start(0), m.end(0)

    def _getMeta(self) -> tuple[str, str, str]:
        """ Return meta data or `config` data. """
        base_url = self.config['base_url']
        end_url = self.config['end_url']
        html_class = self.config['html_class']
        if hasattr(self.md, 'Meta'):
            if 'wiki_base_url' in self.md.Meta:
                base_url = self.md.Meta['wiki_base_url'][0]
            if 'wiki_end_url' in self.md.Meta:
                end_url = self.md.Meta['wiki_end_url'][0]
            if 'wiki_html_class' in self.md.Meta:
                html_class = self.md.Meta['wiki_html_class'][0]
        return base_url, end_url, html_class


def makeExtension(**kwargs):  # pragma: no cover
    return WikiLinkExtension(**kwargs)
