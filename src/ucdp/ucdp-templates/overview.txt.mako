<%!
from aligntext import align
import anytree

class OverviewNode(anytree.NodeMixin):

    def __init__(self, title, overview, children):
        super().__init__()
        self.title = title
        self.overview = overview
        self.children = children



def get_overview_node(mod, minimal=False):
  if not minimal:
    def filter_(node):
      return True
  else:
    def filter_(node):
      return node.get_overview()

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
      yield OverviewNode(f"{mod.name}  {mod}", overview, children)

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
root = get_overview_node(datamodel.top.mod, getattr(datamodel, 'minimal', False))
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
