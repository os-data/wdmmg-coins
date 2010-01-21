<html>

<body>
<% 
	from semantic.utils import render_html
%> 
<table width="100%" border="1">
% for s,p,o in c.triples:
<tr>
    <td>${render_html(s)|n}</td>
    <td>${render_html(p)|n}</td>
    <td>${render_html(o)|n}</td>
</tr>
% endfor
</table>
</body>
</html>
