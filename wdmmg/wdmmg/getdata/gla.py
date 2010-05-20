import os, sys, csv, re
from datetime import date
try: import json
except ImportError: import simplejson as json

import datapkg
from swiss.tabular import gdocs
from pylons import config

import wdmmg.model as model


slice_name = u'gla'
govt_account_name = u'Greater London Authority'
base_url = u'http://legacy.london.gov.uk/gla/expenditure/docs/'


def load_file(fileobj, period_mapper={}, commit_every=None):
    '''
    Loads a file from `fileobj` into a slice with name 'gra'.
    
    fileobj - an open, readable file-like object.
    
    period_mapper - a dict from filename (e.g. u'january_2008.csv') to
        reporting period (e.g. u'2008-01').
    
    commit_every - if not None, call session.model.commit() at the 
        specified frequency.
    '''
    # Semaphore to prevent the data being loaded twice.
    assert not (model.Session.query(model.Slice)
        .filter_by(name=slice_name)
        ).first(), 'GLA already loaded'
    # Make a new slice.
    slice_ = model.Slice(name=slice_name)
    # The keys used to classify spending.
    def mk(name, notes):
        ans = model.Session.query(model.Key).filter_by(name=name).first()
        if not ans:
            ans = model.Key(name=name, notes=notes)
            model.Session.add(ans)
        return ans
    key_spender = mk(u'spender', u'"yes" for the central government account.')
    key_date = mk(u'date', u'''\
The invoice date. Ideally the invoice date would be used as the transaction \
timestamp, but unfortunately it is not always available. In such cases of \
partial data, we consistently use the reporting date, instead of the invoice \
date, as the transaction timestamp. We then use this key to record the invoice \
date.''')
    key_docNumber = mk(u'docNumber', u'The invoice or other document number.')
    key_filename = mk(u'filename', u'''\
The name of the data file in which this spending appears. The URL of the data \
file is formed by prepending %s to the filename.''' % base_url)
    key_rowNumber = mk(u'rowNumber', u'The row number of this spending within its data file.')
    # The central account from which all the money comes.
    acc_govt  = model.Account(
        slice_=slice_, name=govt_account_name)
    acc_govt.keyvalues[key_spender] = u'yes'
    model.Session.add(acc_govt)
    # Utility function for creating Accounts.
    def get_or_create_account(disambiguators, name, index={}):
        if disambiguators not in index:
            index[disambiguators] = model.Account(
                slice_=slice_, name=name, notes=u'')
        return index[disambiguators]
    # Utility function for creating EnumerationValues.
    def get_or_create_value(key, code, name=None, notes=u'', index={}):
        if code not in index:
            index[code] = model.EnumerationValue(
                key=key, code=code, name=name or code, notes=notes)
        # N.B. Not strictly correct to use the same index for all keys,
        # but following assertion has not failed so far.
        assert index[code].key == key
        return index[code]
    # Utility function for parsing numbers.
    def to_float(s):
        if not s: return 0.0
        return float(s.replace(',', ''))
    # For each line of the file...
    reader = csv.reader(fileobj)
    header = reader.next()
#    print header
    for row_index, row in enumerate(reader):
        # Progress output.
        if commit_every and row_index%commit_every == 0:
            print "Committing before processing row %d" % row_index
            model.Session.commit()
        # Parse row.
        if not row[0]:
            # Skip blank row.
            continue
#        print row
        row = [unicode(x.strip()) for x in row]
        amount = to_float(row[0])
        date = row[1] # Often missing.
        description = row[2]
        docNumber = row[3] # Often missing.
        docType = row[4] # Ignore.
        link = row[5]
        rowNumber = row[6]
        supplier = row[7]
        # Computed values.
        assert link.startswith(base_url)
        filename = link[len(base_url):]
        period = period_mapper.get(filename, filename)
        # Ensure all the necessary EnumerationValue objects exist.
        get_or_create_value(key_filename, filename)
        # Make the Account object if necessary.
        dest = get_or_create_account(
            supplier,
            supplier
        )
        # Make the Transaction and its Postings
        txn = model.Transaction.create_with_postings(
            slice_, period, amount, src=acc_govt, dest=dest)
        txn.notes = description
        txn.keyvalues[key_filename] = filename
        txn.keyvalues[key_rowNumber] = rowNumber
        if date:
            txn.keyvalues[key_date] = date
        if docNumber:
            txn.keyvalues[key_docNumber] = docNumber
        model.Session.add(txn)
    if commit_every:
        model.Session.commit()


def drop():
    '''
    Drops from the database all records associated with slice 'cra'.
    '''
    # TODO.
    raise NotImplemented


def load_period_mapper(spreadsheet_key='0AijCXAu1IV6YdDFyYW1VTHJvYXlmQThHQURrQ3VXY1E'):
    '''
    Constructs a dict that maps GLA data file name to reporting period. The
    data is loaded from a Google spreadsheet.
    '''
    ans = {}
    for row in gdocs.GDocsReaderTextDb(spreadsheet_key,
        config['gdocs_username'], config['gdocs_password']
    ).read().to_list()[1:]:
        filename, period, has_dates, has_docNumbers = row
        ans[unicode(filename)] = unicode(period)
    return ans


def load():
    '''
    Downloads the GLA, and loads it into the database with slice name 'gla'.
    Also downloads the mapping from GLA filename to reporting period (month)
    from a Google Documents spreadsheet.
    '''
    # Get the GLA data package.
    pkgspec = 'file://%s' % os.path.join(config['getdata_cache'], 'gla-spending')
    pkg = datapkg.load_package(pkgspec)
    # Load the data.
    load_file(
        pkg.stream('greater-london-assembly-expenditure'),
        load_period_mapper(),
        commit_every=1000
    )
    model.Session.commit()
    model.Session.remove()

