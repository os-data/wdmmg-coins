import pkgutil
from StringIO import StringIO

from wdmmgrdf.tests import *
import wdmmgrdf.model as model
import wdmmgrdf.getdata.cofog as cofog

class TestCofogLoader(object):
    @classmethod
    def teardown_class(self):
        clean_pairtree()

    def test_01(self):
        assert model.handler
        triples = StringIO(pkgutil.get_data('wdmmgrdf', 'tests/indata/cofog.n3'))
        cofog.load_file(triples)
        g = model.handler.get(cofog.COFOG_IDENTIFIER)
        assert len(g) == 20, len(g)

