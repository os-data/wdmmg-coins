from datetime import datetime

import wdmmg.model as model

class TestAccountBasics(object):
    @classmethod
    def setup_class(self):
        self.accsrc = u'acc1'
        self.accdest = u'acc2'
        acc_src = model.Account(name=self.accsrc)
        acc_dest = model.Account(name=self.accdest)
        # transaction has the date?
        txn = model.Transaction.create_with_postings(
            timestamp=datetime.now(),
            amount=1000,
            src=acc_src,
            dest=acc_dest)
        assert txn.postings
        model.Session.add_all([acc_src,acc_dest,txn])
        model.Session.commit()
        model.Session.remove()

    @classmethod
    def teardown_class(self):
        model.repo.delete_all()

    def test_01(self):
        txn = model.Session.query(model.Transaction).first()
        assert txn
        assert len(txn.postings) == 2, txn
        assert self.accsrc in [ posting.account.name for posting in txn.postings ]

    def test_02(self):
        acc_src = model.Session.query(model.Account).filter_by(name=self.accsrc).one()
        acc_dest = model.Session.query(model.Account).filter_by(name=self.accdest).one()
        region = model.Key(name=u'region', description=u'Area for which money was spent')
        pog = model.Key(name=u'pog', description=u'Programme Object Group')
        randomkey = model.Key(name=u'randomkey')

        northwest = model.EnumerationValue(name=u'Northwest', key=region)
        northeast = model.EnumerationValue(name=u'Northeast', key=region)
        pog1 = model.EnumerationValue(name=u'surestart', key=pog)
        pog2 = model.EnumerationValue(name=u'anotherstart', key=pog)

        kv = model.KeyValue(ns=u'account', account=acc_src, key=region,
                value=northwest.name)
        
        acc_src.keyvalues[region] = northeast.name # This should overwrite the KeyValue explicitly constructed above.
        acc_src.keyvalues[randomkey]= u'annakarenina'
        acc_dest.keyvalues[region] = northwest.name

        model.Session.add_all([region,pog,randomkey,kv])
        model.Session.commit()
        model.Session.remove()
        del acc_src, acc_dest, region, pog, randomkey, kv
        
        # Read it all back again.

        pog = model.Session.query(model.Key).filter_by(name=u'pog').one()
        assert pog.description.startswith(u'Programme')
        assert len(pog.enumeration_values) == 2, pog

        region = model.Session.query(model.Key).filter_by(name=u'region').one()
        assert region, region
        region_kvs = model.Session.query(model.KeyValue).filter_by(key=region).all()
        assert len(region_kvs) == 2, region_kvs
        
        acc_src = model.Session.query(model.Account).filter_by(name=self.accsrc).one()
        assert acc_src
        acc_dest = model.Session.query(model.Account).filter_by(name=self.accdest).one()
        assert acc_dest
        
        acc_src_region_kv = model.Session.query(model.KeyValue).filter_by(account=acc_src).filter_by(key=region).one()
        assert acc_src_region_kv.value == u'Northeast'
        assert acc_src._keyvalues[region] == acc_src_region_kv
        assert acc_src.keyvalues[region] == u'Northeast'
        
        assert acc_dest.keyvalues[region] == u'Northwest'



class CRALoader(object):
    '''Load CRA'''

    def create_region(self, name, index={}):
        if name not in index:
            index[name] = Value(name=name)
        return index[name]

    def load(self, fileobj):
        slice = Slice('cra')
        acc_govt  = Account(u'Government (Dummy)')
        region_obj = Key(name='region', description='Area for which money was spent')
        header = reader.next()
        year_col_start = 11
        years = header[year_col_start:]
        for row in reader():
            expenditures = [ float(x) for x in row[year_col_start:] ]
            # expenditures all zero
            if not [ x for x in expenditures if x ]:
                continue
            dest = Account() 
            dest.set(region, create_region(row[10]))
            dest.set(pog, create_pog(row[7]))
            # dest.set(...)
            for year, exp in zip(years, expenditures):
                txn = Transaction.create_with_postings(year, exp, src=acc_govt,
                    dest=dest)

def _test_load_cra():
    fileobj = open('path_to_cra_data')
    out = CRALoader.load(fileobj)

