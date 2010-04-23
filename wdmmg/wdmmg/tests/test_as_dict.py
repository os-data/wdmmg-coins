import wdmmg.model as model
from wdmmg.tests import Fixtures

class TestAsDict(object):
    @classmethod
    def setup_class(self):
        Fixtures.setup()
    
    @classmethod
    def teardown_class(self):
        Fixtures.teardown()
    
    def test_slice(self):
        ans = Fixtures.slice_.as_big_dict()
        for field in ['id', 'name', 'notes']:
            assert field in ans, ans
    
    def test_account(self):
        ans = Fixtures.govt_account.as_big_dict()
        for field in ['id', 'slice', 'name', 'notes', 'keyvalues']:
            assert field in ans, ans
        for field in ['id', 'name']:
            assert field in ans['slice'], ans
        for key in ['spender']:
            assert key in ans['keyvalues'], ans

    def test_transaction(self):
        ans = (model.Session.query(model.Transaction)
            .filter_by(slice_=Fixtures.slice_)
            ).first().as_big_dict()
        for field in ['id', 'slice', 'timestamp', 'notes', 'postings']:
            assert field in ans, ans
        for field in ['id', 'name']:
            assert field in ans['slice'], ans
        for p in ans['postings']:
            for field in ['timestamp', 'account', 'currency', 'amount']:
                assert field in p, p
            for field in ['id', 'name', 'slice_id', 'keyvalues']:
                assert field in p['account'], p

    def test_key(self):
        ans = Fixtures.cofog2.as_big_dict()
        for field in ['id', 'name', 'notes', 'enumeration_values', 'keyvalues']:
            assert field in ans, ans
        evs = ans['enumeration_values']
        for code in [u'04.5']:
            assert code in evs, evs
            for field in ['id', 'key_id', 'code', 'name', 'keyvalues']:
                assert field in evs[code], evs[code]
            for key in ['parent']:
                assert key in evs[code]['keyvalues'], evs[code]
        for key in ['parent']:
            assert key in ans['keyvalues'], ans

    def test_enumeration_value(self):
        ans = (model.Session.query(model.EnumerationValue)
            .filter_by(key=Fixtures.region)
            ).first().as_big_dict()
        for field in ['id', 'key', 'code', 'name', 'notes', 'keyvalues']:
            assert field in ans, ans
        for field in ['id', 'name', 'keyvalues']:
            assert field in ans['key'], ans
        for key in ['population2006']:
            assert key in ans['keyvalues'], ans

