import pkg_resources

import wdmmg.model as model
from wdmmg.getdata.cra import CRALoader


class TestCRALoader(object):
    @classmethod
    def setup_class(self):
        model.repo.delete_all()
        fileobj = pkg_resources.resource_stream('wdmmg', 'tests/cra_2009_db_short.csv')
        CRALoader.load(fileobj)
        model.Session.commit()
        model.Session.remove()

    @classmethod
    def teardown_class(self):
        model.repo.delete_all()
        model.Session.commit()
        model.Session.remove()

    def test_slice(self):
        print 'test_load'
        out = (model.Session.query(model.Slice)
            .filter_by(name=CRALoader.slice_name)
            ).one()
        assert out, out
    
    def test_govt_account(self):
        out = (model.Session.query(model.Account)
            .filter_by(name=CRALoader.govt_account_name)
            ).one()
        assert out, out

    def test_number_of_accounts(self):
        out = model.Session.query(model.Account).count()
        assert out > 5, out
    
    def test_keys(self):
        for key_name in u'dept', u'pog', u'function', u'region':
            out = model.Session.query(model.Key).filter_by(name=key_name).one()
            assert out, key_name

