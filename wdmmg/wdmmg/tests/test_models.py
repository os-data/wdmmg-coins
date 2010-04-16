from datetime import datetime

import wdmmg.model as model

class TestAccountBasics(object):
    @classmethod
    def setup_class(self):
        self.slice_ = u'test'
        self.accsrc = u'acc1'
        self.accdest = u'acc2'
        self.timestamp = datetime.now()
        slice_ = model.Slice(name=self.slice_)
        acc_src = model.Account(slice_=slice_, name=self.accsrc)
        acc_dest = model.Account(slice_=slice_, name=self.accdest)
        # transaction has the date?
        txn = model.Transaction.create_with_postings(
            slice_=slice_,
            timestamp=self.timestamp,
            amount=1000,
            src=acc_src,
            dest=acc_dest)
        assert txn.postings
        model.Session.add_all([slice_, acc_src,acc_dest,txn])
        model.Session.commit()
        model.Session.remove()

    @classmethod
    def teardown_class(self):
        model.repo.delete_all()

    def test_01(self):
        slice_ = model.Session.query(model.Slice).filter_by(name=self.slice_).one()
        txn = (model.Session.query(model.Transaction)
            .filter_by(slice_=slice_)
            .filter_by(timestamp=self.timestamp)).one()
        assert txn
        assert len(txn.postings) == 2, txn
        assert self.accsrc in [ posting.account.name for posting in txn.postings ]

    # TODO: Factor this into multiple tests, with setup done somewhere sensible.
    def test_02(self):
        slice_ = model.Session.query(model.Slice).filter_by(name=self.slice_).one()
        acc_src = (model.Session.query(model.Account)
            .filter_by(slice_=slice_)
            .filter_by(name=self.accsrc)).one()
        acc_dest = (model.Session.query(model.Account)
            .filter_by(slice_=slice_)
            .filter_by(name=self.accdest)).one()
        region = model.Key(name=u'region', notes=u'Area for which money was spent')
        pog = model.Key(name=u'pog', notes=u'Programme Object Group')
        randomkey = model.Key(name=u'randomkey')

        northwest = model.EnumerationValue(name=u'Northwest', key=region)
        northeast = model.EnumerationValue(name=u'Northeast', key=region)
        pog1 = model.EnumerationValue(name=u'surestart', key=pog)
        pog2 = model.EnumerationValue(name=u'anotherstart', key=pog)

        kv1 = model.KeyValue(ns=u'account', ns_account=acc_src, key=region,
                value=northwest.name)
        acc_src.keyvalues[region] = northeast.name # This should overwrite the KeyValue explicitly constructed above.
        acc_src.keyvalues[randomkey]= u'annakarenina' # This should create a new KeyValue.

        kv2 = model.KeyValue(ns=u'account', ns_account=acc_dest, key=randomkey,
                value=u'orangesarenottheonlyfruit') # This one should not get overwritten.
        acc_dest.keyvalues[region] = northwest.name # This should create a new KeyValue.

        model.Session.add_all([region, pog, randomkey, kv1, kv2])
        model.Session.commit()
        model.Session.remove()
        del acc_src, acc_dest, region, pog, randomkey, kv1, kv2
        
        # Read it all back again.

        pog = model.Session.query(model.Key).filter_by(name=u'pog').one()
        assert pog.notes.startswith(u'Programme')
        assert len(pog.enumeration_values) == 2, pog

        region = model.Session.query(model.Key).filter_by(name=u'region').one()
        assert region
        region_kvs = model.Session.query(model.KeyValue).filter_by(key=region).all()
        assert len(region_kvs) == 2, region_kvs
        
        randomkey = model.Session.query(model.Key).filter_by(name=u'randomkey').one()
        assert randomkey

        acc_src = model.Session.query(model.Account).filter_by(name=self.accsrc).one()
        assert acc_src
        acc_dest = model.Session.query(model.Account).filter_by(name=self.accdest).one()
        assert acc_dest
        
        northeast = model.Session.query(model.EnumerationValue).filter_by(key=region).filter_by(name=u'Northeast').one()
        assert northeast.key == region, northest.key
        assert northeast.name == u'Northeast', northeast.name
        
        acc_src_region_kv = model.Session.query(model.KeyValue).filter_by(ns_account=acc_src).filter_by(key=region).one()
        assert acc_src_region_kv.value == u'Northeast'
        assert acc_src_region_kv.enumeration_value == northeast, acc_src_region_kv.enumeration_value
        assert acc_src._keyvalues[region] == acc_src_region_kv
        assert acc_src.keyvalues[region] == u'Northeast'
        assert acc_src.keyvalues[randomkey] == u'annakarenina'
        
        assert acc_dest.keyvalues[region] == u'Northwest'
        assert acc_dest.keyvalues[randomkey] == u'orangesarenottheonlyfruit'
        
        # Test purging of KeyValues.
        before_count = model.Session.query(model.KeyValue).count()
        acc_src.keyvalues = {}
        model.Session.commit()
        model.Session.remove()
        
        acc_src = model.Session.query(model.Account).filter_by(name=self.accsrc).one()
        assert not acc_src.keyvalues
        print [str(x) for x in model.Session.query(model.KeyValue).all()]
        after_count = model.Session.query(model.KeyValue).count()
        assert before_count > after_count, (before_count, after_count)
        
