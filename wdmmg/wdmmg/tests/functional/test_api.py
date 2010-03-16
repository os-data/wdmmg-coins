from wdmmg.tests import *

class TestApiController(TestController):

    def _test_index(self):
        response = self.app.get(url(controller='api', action='index'))
        # Test response...
