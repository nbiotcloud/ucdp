<%!
from aligntext import align
import anytree
import ucdp as u

class OverviewNode(anytree.NodeMixin):

    def __init__(self, title, overview, children, tags):
        super().__init__()
        self.title = title
        self.overview = overview
        self.children = children
        self.tags = tags



def get_overview_node(mod, minimal=False, tags=None):
  tagfilter = u.namefilter(tags)
  if not minimal:
    def filter_(node):
      return any(tagfilter(tag) for tag in node.tags)
  else:
    def filter_(node):
      if any(tagfilter(tag) for tag in node.tags):
        return node.get_overview()
      return None

  nodes = tuple(_iter_overview_nodes([mod], filter_))

  if nodes:
    return nodes[0]

def _iter_overview_nodes(mods, filter_):
  for mod in mods:
    overview = None
    if filter_(mod):
       overview = mod.get_overview()

    children = tuple(_iter_overview_nodes(mod.insts, filter_))

    if overview is not None or children:
      yield OverviewNode(f"{mod.name}  {mod}", overview, children, mod.tags)

def iter_rect(overview):
  lines = align([("| ", row, " |") for row in overview.split("\n")]).split("\n")
  linelen = len(lines[0]) - 2
  dashes = "-" * linelen
  spaces = " " * linelen
  yield f"+{dashes}+"
  yield f"|{spaces}|"
  yield from lines
  yield f"|{spaces}|"
  yield f"+{dashes}+"


%>\
<%
minimal = getattr(datamodel, 'minimal', False)
tags = getattr(datamodel, 'tags', None)
root = get_overview_node(datamodel.top.mod, minimal=minimal, tags=tags)
%>\
% if root:
%   for pre, fill, node in anytree.RenderTree(root):
${pre}${node.title}
%     if node.overview:
%       for line in iter_rect(node.overview):
${fill}${line}
%       endfor
%     endif
%   endfor
% else:
No overview available.
% endif
