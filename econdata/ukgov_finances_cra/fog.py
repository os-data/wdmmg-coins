from data import dburi
from db import Repository, Session
from sys import stderr
import re

_uncode_re = re.compile(r"^(?P<code>[0-9][0-9.]*) (?P<descr>.*)")
def match_uncode(function, subfunction):
	fm = _uncode_re.match(function)
	sm = _uncode_re.match(subfunction)
	if fm and sm:
		fd = fm.groupdict()
		sd = sm.groupdict()
		code = fd["code"] if (fd["code"] and len(fd["code"]) > len(sd["code"])) else sd["code"]
	elif fm:
		fd = fm.groupdict()
		code = fd["code"]
	elif sm:
		sd = sm.groupdict()
		code = sd["code"]
	else:
		code = ""
	code = code.rstrip(".")
	if len(code) > 1 and code[1] == ".":
		code = "0" + code
	return code

def match_fog(function, subfunction):
	return match_uncode(function, subfunction)
	
if __name__ == "__main__":
	Repository(dburi)
	cursor = Session.connection()
	q = """\
	SELECT DISTINCT function, subfunction
	FROM area
	GROUP BY function, subfunction
	"""
	for function, subfunction in cursor.execute(q):
		code = match_fog(function, subfunction)
		print (code, function, subfunction)
