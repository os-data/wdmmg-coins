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
        example = (model.Session.query(model.EnumerationValue)
            .filter_by(key=Fixtures.dept)
            .filter_by(code=u'Dept004')
            ).one()
        response = self.app.get(url(controller='enumeration_value', action='view',
            id_=example.id))
        assert '''dept''' in response, response
        assert '''Dept004''' in response, response
        assert '''Department for Transport''' in response, response

