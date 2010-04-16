import os, sys, csv, json, re
from datetime import date

import datapkg
from pylons import config

import wdmmg.model as model

class CofogMapper(object):
    '''
    In the published data, the "function" and "subfunction" columns are used
    inconsistently. This is partly because some departments continue to use a
    previous coding system, and partly because only two columns have been
    allowed for the three levels of the COFOG hierarchy.
    
    This class uses a mapping provided by William Waites to work out the
    correct COFOG code, given the published data.
    '''
    def __init__(self, mappings):
        '''
        Constructs a COFOG mapper given a JSON file of mappings.
        
        mappings - a list of triples. In each
            triple, the first element is the good code, and the second and
            third elements give the published values. If the first element
            (the good code) contains non-numerical suffix, it will be removed.
        '''
        self.mappings = {}
        for good, bad1, bad2 in mappings:
            good = re.match(r'([0-9]+(\.[0-9])*)', good).group(1)
            self.mappings[bad1, bad2] = good
    
    def fix(self, function, subfunction):
        '''
        Looks up the fixed COFOG code given the published values.
        
        Returns a list giving all available COFOG levels, e.g.
        `[u'01', u'01.1', u'01.1.1']`
        '''
        ans = self.mappings[function, subfunction]
        parts = ans.split('.')
        return ['.'.join(parts[:i+1]) for i, _ in enumerate(parts)]

# TODO: There's no need for this to be a class.
class CRALoader(object):
    '''Load CRA'''
    
    slice_name = u'cra'
    govt_account_name = u'Government (Dummy)'
    
    @classmethod
    def load(self, fileobj, cofog_mapper, commit_every=None):
        '''
        Loads a file from `fileobj` into a slice with name 'cra'.
        The file should be CSV formatted, with the same structure as the 
        Country Regional Analysis data.
        
        fileobj - an open, readable file-like object.
        
        commit_every - if not None, call session.model.commit() at the 
            specified frequency.
        '''
        # Semaphore to prevent the data being loaded twice.
        assert not (model.Session.query(model.Slice)
            .filter_by(name=CRALoader.slice_name)
            ).first(), 'CRA already loaded'
        # Semaphore to ensure COFOG is loaded first.
        assert (model.Session.query(model.Key)
            .filter_by(name='cofog1')
            ).first(), 'COFOG must be loaded first'
        # Make a new slice.
        slice_ = model.Slice(name=CRALoader.slice_name)
        # The keys used to classify spending.
        def mk(name, notes):
            return model.Key(name=name, notes=notes)
        key_spender = mk(u'spender', u'"yes" for the central government account')
        key_dept = mk(u'dept', u'Department that spent the money')
        key_pog = mk(u'pog', u'Programme Object Group')
        key_cap_or_cur = mk(u'cap_or_cur', u'Capital or Current')
        key_region = mk(u'region', u'Geographical (NUTS) area for which money was spent')
        model.Session.add_all([key_spender, key_dept, key_pog, key_cap_or_cur,
            key_region])
        # We also use 'cofog1', 'cofog2' and 'cofog3' from the COFOG package.
        key_cofog1 = model.Session.query(model.Key).filter_by(name=u'cofog1').one()
        key_cofog2 = model.Session.query(model.Key).filter_by(name=u'cofog2').one()
        key_cofog3 = model.Session.query(model.Key).filter_by(name=u'cofog3').one()
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
        # TODO: Represent dates as opaque unicode strings.
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
            get_or_create_value(key_pog, pog, pog_alias)
            get_or_create_value(key_cap_or_cur, cap_or_cur)
            get_or_create_value(key_region, region)
            cofog_parts = cofog_mapper.fix(function, subfunction)
            assert cofog_parts, 'COFOG code is missing'
            assert len(cofog_parts) <= 3, 'COFOG code has too many levels'
                
            # TODO: Preserve the published function and subfunction in the notes field.

            # Make the Account object if necessary.
            dest = get_or_create_account(
                (deptcode, function, subfunction, pog, cap_or_cur, region),
                u'{Dept="%s", function="%s", region="%s"}' % (dept, function, region)
            )
            dest.keyvalues[key_dept] = deptcode
            dest.keyvalues[key_pog] = pog
            dest.keyvalues[key_cap_or_cur] = cap_or_cur
            dest.keyvalues[key_region] = region
            if len(cofog_parts) >= 1:
                dest.keyvalues[key_cofog1] = cofog_parts[0]
            if len(cofog_parts) >= 2:
                dest.keyvalues[key_cofog2] = cofog_parts[1]
            if len(cofog_parts) >= 3:
                dest.keyvalues[key_cofog2] = cofog_parts[2]
            
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
    # Delete only the keys we created ourselves.
    # TODO: Move as many as possible of these into separate data packages.
    for name in ['dept', 'function', 'subfunction', 'pog', 'cap_or_cur', 'region']:
        key = (model.Session.query(model.Key)
            .filter_by(name=name)
            ).one()
        assert key, name
        key.keyvalues.clear()
        model.Session.delete(key)
    # Delete ATP structure.
    # TODO: ORM-ise this code.
    slice_ = (model.Session.query(model.Slice)
        .filter_by(name=u'cra')
        ).one()
    assert slice_
    (model.Session.query(model.KeyValue)
        .join(model.Posting)
        .filter(model.KeyValue.object_id == model.Posting.id)
        .filter_by(ns='posting')
        .join(model.Account)
        .filter_by(slice_=slice_)
        ).delete()
    (model.Session.query(model.Posting)
        .join(model.Account)
        .filter_by(slice_=slice_)
        ).delete()
    (model.Session.query(model.KeyValue)
        .join(model.Account)
        .filter_by(slice_=slice_)
        ).delete()
    (model.Session.query(model.Account)
        .filter_by(slice_=slice_)
        ).delete()
    (model.Session.query(model.KeyValue)
        .join(model.Transaction)
        .filter_by(slice_=slice_)
        ).delete()
    (model.Session.query(model.Transaction)
        .filter_by(slice_=slice_)
        ).delete()
    model.Session.delete(slice_)

def load():
    '''
    Downloads the CRA, and loads it into the database with slice name 'cra'.
    '''
    # Get the CRA data package.
    indexpath = config['getdata_cache']
    pkgname = 'ukgov_finances_cra'
    # could just use pkg path ...
    pkgspec = 'file://%s' % os.path.join(indexpath, pkgname)
    pkg = datapkg.load_package(pkgspec)
    # Make a CofogMapper.
    cofog_mapper = CofogMapper(json.load(pkg.stream('cofog_map.json')))
    # Load the data.
    CRALoader.load(pkg.stream('cra_2009_db.csv'), cofog_mapper, commit_every=100)
    model.Session.commit()
    model.Session.remove()

