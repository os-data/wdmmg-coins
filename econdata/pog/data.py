#!/usr/bin/env python
# data.py
# David Jones, david.jones@okfn.org, 2010-05-25

"""
Scrapes the output of the OCR'd documents received from HM Treasury, and
outputs machine readable POG data.
"""

# http://docs.python.org/release/2.5.4/lib/module-re.html
import re
# okfn
import swiss
cache = swiss.Cache('cache')

url = "http://www.archive.org/download/PogAndPo_138/POG-to-PO.zip"

# Various regular expressions used by the parser.

# RE for removing OCR dirt from the beginnings or ends of lines:
# Extremely pragmatic.
dirt = '(\w?[^\w]+|\w|to)'
dirtre = '(^' + dirt + '($| +))|(\s+' + dirt + '$)'

# Regular expression for 10 character code.  Example:
# "P01 S100101"
# (These are POG codes, but this program doesn't really care).
code10re = r'P\w\w ?[S5]\w{6}'
# RE for 8 character code.  Example:
# "P0110001"
# (These are PO codes, but again, we don't really care).
code8re = r'P\w{6}\s?\w'
# RE for 3 character code.  Example:
# P01
# (These are PO Prefix codes)
code3re = r'P\w\w(?=\sPO)'
# Regular expression for header line.
# These are generally of the form 
# "Code Description Parent", but a couple of files have some junk first.
headre = r'.{,6}Code'
# RE for line number
linenore = r'^\d+$'

class Loader(object):
    def retrieve(self, args):
        '''Retrieve the POG data to cache (if not already there)'''
        cache.retrieve(url)

    def parse1(self, args):
        '''Parse one file from the cache.'''
        # http://docs.python.org/release/2.5.4/lib/module-os.path.html
        import os.path
        # http://docs.python.org/release/2.5.4/lib/module-csv.html
        import csv
        n = args[1]
        inp = open(os.path.join('cache', 'POG-to-PO', '%s.txt' % n), 'Ur')

        out = open('pog.csv', 'w')
        acsv = csv.writer(out)

        rxlist = [
              ('POG', code10re),
              ('PO', code8re),
              ('head', headre),
              ('POPrefix', code3re),
              ('lineno', linenore),
              ]

        result = dict(((cat,[]) for cat,_ in rxlist))
        result['nocat'] = []
        for line in inp:
            # Each line has some fairly dumb low level cleanup before we
            # attempt to work out if it is PO, POG, etc.
            # Remove dirt and other junk
            line = re.sub(dirtre, '', line)
            # Remove spurious OCR spaces following a 1.  We remove a
            # space if it follows a 1 and is followed by a digit.
            line = re.sub(r'(1) (?=\d)', r'\1', line)
            # A "7" is often scanned as a "?".
            # Replace any "?" that is either followed by or preceded by
            # a number, with a '7'.
            line = re.sub(r'((?<=\d)\?)|(\?(?=\d))', '7', line)

            for cat,rx in rxlist:
                m = re.match(rx, line)
                if m:
                    code = m.group()
                    rest = line[m.end():].strip()
                    corrections = ''
                    # Make the space in *code* canonical:
                    # Pxx Sxxxxxx
                    code = code.replace(' ', '')
                    if cat == 'code10':
                        code = code[:3] + ' ' + code[3:]
                    t = (code, rest)
                    result[cat].append(code)
                    
                    # We're not interested in printing out the
                    # "Code/Description/Parent" lines all the time.
                    if cat in ('head', 'lineno'):
                        break
                    # Should be type, code, description, parent.
                    acsv.writerow([cat, code, rest, ""])
                    break
            else:
                # Didn't match againgst any RE.
                acsv.writerow(['unknown', line])

        del acsv
        out.close()
        return

import optparse
import os
import sys
import inspect
def _extract(obj):
    methods = inspect.getmembers(obj, inspect.ismethod)
    methods = filter(lambda (name,y): not name.startswith('_'), methods)
    methods = dict(methods)
    return methods

def main():
    _methods = _extract(Loader)

    usage = '''%prog {action}

    '''
    usage += '\n    '.join(
        [ '%s: %s' % (name, m.__doc__.split('\n')[0] if m.__doc__ else '') for (name,m)
        in _methods.items() ])
    parser = optparse.OptionParser(usage)

    options, args = parser.parse_args()
    if not args or not args[0] in _methods:
        parser.print_help()
        sys.exit(1)

    method = args[0]
    getattr(Loader(), method)(args)


if __name__ == '__main__':
    main()
