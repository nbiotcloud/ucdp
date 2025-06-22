<%!
from aligntext import align
import anytree

import ucdp as u

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
root = u.get_overview_tree(datamodel.top.mod, minimal=minimal, tags=tags)
%>\
% if root:
%   for pre, fill, node in anytree.RenderTree(root, style=anytree.AsciiStyle()):
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
