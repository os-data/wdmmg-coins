import pkgutil

import wdmmgrdf.model as model
import wdmmgrdf.getdata.cofog as cofog

class TestCofogLoader(object):
    def test_01(self):
        # cofog.load_file(pkg_resources.resource_stream('wdmmg', 'tests/COFOG_english_structure_short.txt'))
        # model.handler
        assert model.handler
        # loader = cofog.Loader()
        cofog.load_file(pkgutil.get_data('wdmmg', 'tests/COFOG_english_structure_short.txt'))

