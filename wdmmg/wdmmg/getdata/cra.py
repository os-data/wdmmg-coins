from datetime import date
import csv

import wdmmg.model as model

class CRALoader(object):
    '''Load CRA'''
    
    slice_name = u'cra'
    govt_account_name = u'Government (Dummy)'
    
    @classmethod
    def load(self, fileobj, commit_every=None):
        '''
        Loads a file from `fileobj` into a slice with name 'cra'.
        The file should be CSV formatted, with the same structure as the 
        Country Regional Analysis data.
        
        fileobj - an open, readable file-like object.
        
        commit_every - if not None, call session.model.commit() at the 
            specified frequency.
        '''
        # Make a new slice. This also prevents the data being loaded twice.
        slice_ = model.Slice(name=CRALoader.slice_name)
        # The keys used to classify spending.
        def mk(name, notes):
            return model.Key(
#                slice_=slice_,
                name=name, notes=notes)
        key_spender = mk(u'spender', u'"yes" for the central government account')
        key_dept = mk(u'dept', u'Department that spent the money')
        key_function = mk(u'function', u'COFOG function (purpose of spending)')
        key_subfunction = mk(u'subfunction', u'COFOG sub-function (purpose of spending)')
        key_pog = mk(u'pog', u'Programme Object Group')
        key_cap_or_cur = mk(u'cap_or_cur', u'Capital or Current')
        key_region = mk(u'region', u'Geographical (NUTS) area for which money was spent')
        model.Session.add_all([key_spender, key_dept, key_function,
            key_subfunction, key_pog, key_cap_or_cur, key_region])
        # The central account from which all the money comes.
        acc_govt  = model.Account(
            slice_=slice_, name=CRALoader.govt_account_name)
        acc_govt.keyvalues[key_spender] = u'yes'
        model.Session.add(acc_govt)
        # Utility function for creating Accounts.
        def get_or_create_account(disambiguators, name, index={}):
            if disambiguators not in index:
                index[disambiguators] = model.Account(
                    slice_=slice_, name=name, notes=u'')
            return index[disambiguators]
        # Utility function for creating EnumerationValues.
        def get_or_create_value(key, name, notes=None, index={}):
            if name not in index:
                index[name] = model.EnumerationValue(key=key, name=name, notes=notes)
            return index[name]
        # Utility function for parsing numbers.
        def to_float(s):
            if not s: return 0.0
            return float(s.replace(',', ''))
        # For each line of the file...
        reader = csv.reader(fileobj)
        header = reader.next()
        year_col_start = 10
        years = [date(int(x[:4]), 4, 5) # TBC: Periods start on 5th April
          for x in header[year_col_start:]]
        for row_index, row in enumerate(reader):
            # Progress output.
            if commit_every and row_index%commit_every == 0:
                print "Committing before processing row %d" % row_index
                model.Session.commit()
            # Parse row.
            if not row[0]:
                # Skip blank row.
                continue
            row = [unicode(x.strip()) for x in row]
            deptcode = row[0]
            dept = row[1] # Verbose form of `deptcode`
            function = row[2]
            subfunction = row[3]
            pog = row[4]
            pog_alias = row[5] # Verbose form of `pog`.
            cap_or_cur = row[7]
            region = row[9]
            expenditures = [to_float(x) for x in row[year_col_start:]]
            if not [ x for x in expenditures if x ]:
                # Skip row whose expenditures are all zero.
                continue

            # Ensure all the necessary EnumerationValue objects exist.
            get_or_create_value(key_dept, deptcode, dept)
            # TODO: Use William Waites' coding of functions and subfunctions.
            get_or_create_value(key_function, function)
            get_or_create_value(key_subfunction, subfunction)
            # TODO: Use a KeyValue to relate subfunctions to functions.
            get_or_create_value(key_pog, pog, pog_alias)
            get_or_create_value(key_cap_or_cur, cap_or_cur)
            get_or_create_value(key_region, region)

            # Make the Account object if necessary.
            dest = get_or_create_account(
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
                    txn = model.Transaction.create_with_postings(
                        slice_, year, exp, src=acc_govt, dest=dest)
                    model.Session.add(txn)
        if commit_every:
            model.Session.commit()

def drop():
    '''
    Drops from the database all records associated with slice 'cra'.
    '''
    # FIXME: Do this properly.
    model.repo.delete_all()
    model.Session.commit()
    model.Session.remove()

def load():
    '''
    Downloads the CRA, and loads it into the database with slice name 'cra'.
    '''
    import swiss
    cache = swiss.Cache(path='/tmp/')
    filename = cache.retrieve('http://www.hm-treasury.gov.uk/d/cra_2009_db.csv')
    fileobj = open(filename)
    CRALoader.load(fileobj, commit_every=100)
    model.Session.commit()
    model.Session.remove()

