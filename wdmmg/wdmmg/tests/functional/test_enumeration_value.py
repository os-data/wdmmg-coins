from wdmmg.tests import *
from wdmmg import model

class TestEnumerationValueController(TestController):

    @classmethod
    def setup_class(self):
        Fixtures.setup()
    
    @classmethod
    def teardown_class(self):
        Fixtures.teardown()

    def test_view(self):
        response = self.app.get(url(controller='enumeration_value', action='view',
            name_or_id=Fixtures.dept.name, code=u'Dept004'))
        assert '''dept''' in response, response
        assert '''Dept004''' in response, response
        assert '''Department for Transport''' in response, response

