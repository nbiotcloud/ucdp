<%inherit file="main.mako"/>

<%def name="content(arg=None)">\
${arg}
% for name, value in datamodel.__dict__.items():
${name}: ${value}
% endfor
</%def>

<%block name="main">\
${content()}
${content('again')}
</%block>\
