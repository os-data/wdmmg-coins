from wdmmg.tests import *

class TestHomeController(TestController):
    @classmethod
    def setup_class(self):
        Fixtures.setup()

    @classmethod
    def teardown_class(self):
        Fixtures.teardown()

    def test_index(self):
        response = self.app.get(url('home'))
        assert 'Where Does My Money Go' in response

    def test_index_links(self):
        response = self.app.get(url('home'))
        assert '1 slice(s)' in response, response
        assert '9 accounts' in response
        res2 = response.click('1 slice.*')
        assert 'All slices' in res2

