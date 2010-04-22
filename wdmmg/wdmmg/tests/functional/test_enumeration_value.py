from wdmmg.tests import *

class TestEnumerationValueController(TestController):

    @classmethod
    def setup_class(self):
        Fixtures.setup()
    
    @classmethod
    def teardown_class(self):
        Fixtures.teardown()

    def test_view(self):
        response = self.app.get(url(controller='enumeration_value', action='view',
            key_id=Fixtures.dept.id, code='Dept004'))
        assert '''dept''' in response, response
        assert '''Dept004''' in response, response
        assert '''Department for Transport''' in response, response

