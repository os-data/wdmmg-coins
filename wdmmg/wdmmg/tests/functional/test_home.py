from wdmmg.tests import *

class TestHomeController(TestController):

    def test_index(self):
        response = self.app.get(url('home'))
        assert 'Where Does My Money Go' in response

