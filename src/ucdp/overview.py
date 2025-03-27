#
# MIT License
#
# Copyright (c) 2024-2025 nbiotcloud
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

"""Overview."""

import anytree

from .iterutil import namefilter


class OverviewNode(anytree.NodeMixin):
    """Overview Node."""

    def __init__(self, title, overview, children, tags):
        super().__init__()
        self.title = title
        self.overview = overview
        self.children = children
        self.tags = tags


def get_overview_tree(mod, minimal=False, tags=None) -> OverviewNode | None:
    """Determine Overview Tree."""
    if minimal:
        if tags:
            # minimal + tags
            tagfilter = namefilter(tags)

            def filter_(node) -> bool:
                return bool(node.tags) and any(tagfilter(tag) for tag in node.tags) and bool(node.get_overview())
        else:
            # minimal
            def filter_(node) -> bool:
                return bool(node.get_overview())
    elif tags:
        # tags
        tagfilter = namefilter(tags)

        def filter_(node) -> bool:
            return bool(node.tags) and any(tagfilter(tag) for tag in node.tags)
    else:

        def filter_(node) -> bool:
            return True

    nodes = tuple(_iter_overview_nodes([mod], filter_))

    if nodes:
        return nodes[0]
    return None


def _iter_overview_nodes(mods, filter_):
    for mod in mods:
        overview = None
        if filter_(mod):
            overview = mod.get_overview()

        children = tuple(_iter_overview_nodes(mod.insts, filter_))

        if overview is not None or children:
            yield OverviewNode(f"{mod.name}  {mod}", overview, children, mod.tags)
