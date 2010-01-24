<%inherit file="/base.mako" />
<%def name="title()">Comprehensive Knowledge Archive Network</%def>
<%def name="body()">
<% 
	from semantic.utils import render_html
%> 
% if c.warnings:
<div id="warnings">
  <ul>
% for warning in c.warnings:
    <li>${warning}</li>
% endfor
  </ul>
</div>
% endif
<table width="100%" border="1">
% for s,p,o in c.triples:
<tr>
    <td>${render_html(s)|n}</td>
    <td>${render_html(p)|n}</td>
    <td>${render_html(o)|n}</td>
</tr>
% endfor
</table>
</%def>
