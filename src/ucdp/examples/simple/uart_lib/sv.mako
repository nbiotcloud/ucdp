<%inherit file="main.mako"/>


<%block name="main">\

${self.header()}\

// Main Content

${self.footer()}\

</%block>


<%def name="header()">\
// Header
</%def>

<%def name="footer()">\
// Footer
</%def>

<%def name="create_inplace()">\
// GENERATE INPLACE BEGIN header()
// GENERATE INPLACE END header

// Inplace Content

// GENERATE INPLACE BEGIN header()
// GENERATE INPLACE END header
</%def>
