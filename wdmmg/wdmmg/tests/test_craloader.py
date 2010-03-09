from datetime import date
import os, sys, csv
import pkg_resources

import wdmmg.model as model

class CRALoader(object):
    '''Load CRA'''

    @classmethod
    def get_or_create_account(self, disambiguators, name, index={}):
        if disambiguators not in index:
            index[disambiguators] = model.Account(name=name, notes=u'')
        return index[disambiguators]
    
    @classmethod
    def get_or_create_value(self, key, name, notes=None, index={}):
        if name not in index:
            index[name] = model.EnumerationValue(key=key, name=name, notes=notes)
        return index[name]

    @classmethod
    def load(self, fileobj):
        # TODO: slice = Slice('cra')
        # The central account from which all the money comes.
        acc_govt  = model.Account(name=u'Government (Dummy)')
        # The keys used to classify spending.
        key_dept = model.Key(name=u'dept', notes=u'Department that spent the money')
        key_function = model.Key(name=u'function', notes=u'COFOG function (purpose of spending)')
        key_subfunction = model.Key(name=u'subfunction', notes=u'COFOG sub-function (purpose of spending)')
        key_pog = model.Key(name=u'pog', notes=u'Programme Object Group')
        key_cap_or_cur = model.Key(name=u'cap_or_cur', notes=u'Capital or Current')
        key_region = model.Key(name=u'region', notes=u'Geographical (NUTS) area for which money was spent')
        model.Session.add_all([key_dept, key_function, key_subfunction,
            key_pog, key_cap_or_cur, key_region])
        model.Session.add(acc_govt)

        # For each line of the file...
        reader = csv.reader(fileobj)
        header = reader.next()
        year_col_start = 10
        years = [date(int(x[:4]), 4, 5) # TBC: Periods start on 5th April
          for x in header[year_col_start:]]
        for row_index, row in enumerate(reader):
            if not row[0]:
                # Skip blank row.
                continue
            row = [unicode(x.strip()) for x in row]
            deptcode = row[0]
            dept = row[1] # Verbose form of `deptcode`
            function = row[2]
            subfunction = (function, row[3])
            pog = row[4]
            pog_alias = row[5] # Verbose form of `pog`.
            cap_or_cur = row[7]
            region = row[9]
            expenditures = [x and float(x) or 0. for x in row[year_col_start:]]
            if not [ x for x in expenditures if x ]:
                # Skip row whose expenditures are all zero.
                continue

            # Ensure all the necessary EnumerationValue objects exist.
            CRALoader.get_or_create_value(key_dept, deptcode, dept)
            # TODO: Use William Waites' coding of functions and subfunctions.
            CRALoader.get_or_create_value(key_function, function)
            CRALoader.get_or_create_value(key_subfunction, subfunction)
            # TODO: Use a KeyValue to relate subfunctions to functions.
            CRALoader.get_or_create_value(key_pog, pog, pog_alias)
            CRALoader.get_or_create_value(key_cap_or_cur, cap_or_cur)
            CRALoader.get_or_create_value(key_region, region)

            # Make the Account object if necessary.
            dest = CRALoader.get_or_create_account(
                (deptcode, function, subfunction, pog, cap_or_cur, region),
                u'{Dept="%s", function="%s", region="%s"}' % (dept, function, region)
            )
            dest.keyvalues[key_dept] = deptcode
            dest.keyvalues[key_function] = function
            dest.keyvalues[key_subfunction] = subfunction
            dest.keyvalues[key_pog] = pog
            dest.keyvalues[key_cap_or_cur] = cap_or_cur
            dest.keyvalues[key_region] = region
            
            # Make a Transaction for each non-zero expenditure.
            for year, exp in zip(years, expenditures):
                if exp:
                    txn = model.Transaction.create_with_postings(year, exp,
                        src=acc_govt, dest=dest)
                    print txn
                    model.Session.add(txn)
        model.Session.commit()
        model.Session.remove()

def test_load_cra():
    # Test data is located in same directory as this script.
    fileobj = pkg_resources.resource_stream('wdmmg', 'tests/cra_2009_db_short.csv')
    out = CRALoader.load(fileobj)
    model.repo.delete_all()

