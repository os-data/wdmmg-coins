<html>

<% 
	from semantic.utils import render_html
%>
<body>
<form method="POST">
<textarea name="query" cols="80" rows="15">
${c.query}
</textarea><br />
<input type="submit" value="Run Query" />
</form>

% if c.error:
<pre>${c.error}</pre>
% endif

<table width="100%" border="1">
<tr>
% for b in c.bindings:
<th>${b}</th>
% endfor
</tr>
% for row in c.results:
<tr>
% for b in c.bindings:
  <td>${render_html(row[b])|n}</td>
% endfor
</tr>
% endfor

</table>

</body>
</html>
