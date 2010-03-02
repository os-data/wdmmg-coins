from datetime import datetime

import wdmmg.model as model

class TestAccountBasics(object):
    @classmethod
    def setup_class(self):
        self.accname = u'acc1'
        acc_src = model.Account(name=self.accname)
        acc_dest = model.Account(name=u'acc2')
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
        assert self.accname in [ posting.account.name for posting in txn.postings ]

    def _test_02(self):
        region = model.Key(name='region', description='Area for which money was spent')
        northwest = model.Value(name='Northwest')

        acc_src.set(region, northwest)
        # behind the scenes
        KeyValue(ns='Account', object_id=acc_src.id, key='region',
            value='scotland')
        # we'd like both key and value to be foreign keys

        # enumerated list ...
        acc.pog_code = 'xxx'

        # ....
        acc.my_fancy_name = 'jones'


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

