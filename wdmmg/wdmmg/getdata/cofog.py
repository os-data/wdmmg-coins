from datetime import date
from zipfile import ZipFile
from StringIO import StringIO
import os, csv

import datapkg
from swiss.tabular import gdocs
from pylons import config

import wdmmg.model as model

def drop():
    '''
    Drops Keys 'cofog1', 'cofog2' and 'cofog3' and all associated
    EnumerationValues and KeyValues.
    
    Does not drop Key 'parent'.
    
    Aborts if Keys are in use (as predicates).
    '''
    # Semaphore to avoid corrupting other data sets: check that Keys are not in use.
    for name in [u'cofog3', u'cofog2', u'cofog1']:
        assert (model.Session.query(model.KeyValue)
            .join(model.Key)
            .filter(model.Key.name == name)
            ).count() == 0, name
    # Delete Keys.
    for name in [u'cofog3', u'cofog2', u'cofog1']:
        print 'Deleting key', name
        key = model.Session.query(model.Key).filter_by(name=name).first()
        if key:
            key.keyvalues.clear() # TODO: Work out how to make this automatic.
            model.Session.delete(key)
    model.Session.commit()
    model.Session.remove()

def load():
    '''
    Downloads the COFOG list, and loads it into the database with key names
    'cofog1', 'cofog2' and 'cofog3'.
    '''
    # Get the COFOG data package.
    pkgspec = 'file://%s' % os.path.join(config['getdata_cache'], 'cofog')
    pkg = datapkg.load_package(pkgspec)
    fileobj = pkg.stream('cofog.csv')
    load_file(fileobj)

def dejargonise():
    '''
    Downloads alternative names for the COFOG codes, chosen specially for WDMMG,
    and replaces the names in the database. The original names are backed up.
    '''
    keys = [model.Session.query(model.Key).filter_by(name=name).one()
        for name in u'cofog1', u'cofog2', u'cofog3']
    # Create the 'official_name' Key if necessary.
    key_official_name = (model.Session.query(model.Key)
        .filter_by(name=u'official_name')
        ).first()
    if not key_official_name:
        key_official_name = model.Key(name=u'official_name', notes=u'''\
The official names of things, as defined by the relevant standards body. We \
do not always use the official names for things, because they are sometimes \
difficult to understand. When we substitute an alternative name, we record \
the official name using this key.''')
        model.Session.add(key_official_name)
    # Loop through the rows of the Google spreadsheet where the data is maintained.
    for row in gdocs.GDocsReaderTextDb(
        'tQSJ9dxTh8AKl-ON4Qqja8Q', # Google spreadsheet key.
        config['gdocs_username'],
        config['gdocs_password']
    ).read().to_list()[2:]:
#        print row
        code, official_name, alternative_name, notes = row
        ev = (model.Session.query(model.EnumerationValue)
            .filter(model.EnumerationValue.key_id.in_([k.id for k in keys]))
            .filter_by(code=unicode(code))
            ).first()
        assert ev, 'Spreadsheet contains an unknown COFOG code: %r' % row
        if alternative_name:
            print "Setting name of %r to %r" % (code, alternative_name)
            if key_official_name not in ev.keyvalues:
                # Make a backup of the official name.
                # assert ev.name == official_name
                ev.keyvalues[key_official_name] = ev.name
            ev.name = unicode(alternative_name)
    model.Session.commit()
    model.Session.remove()

def load_file(fileobj):
    '''
    Loads the specified COFOG-like file into the database with key names
    'cofog1', 'cofog2' and 'cofog3'.
    '''
    # Semaphore to avoid creating multiple copies.
    assert not model.Session.query(model.Key).filter_by(name=u'cofog1').first(), "COFOG already loaded"
    # Create the 'parent' Key if necessary.
    key_parent = model.Session.query(model.Key).filter_by(name=u'parent').first()
    if not key_parent:
        key_parent = model.Key(name=u'parent', notes=u'Means "is part of".')
        model.Session.add(key_parent)
    # Create the COFOG Keys.
    key_cofog1 = model.Key(name=u'cofog1', notes=u'Classification Of Function Of Government, level 1')
    key_cofog2 = model.Key(name=u'cofog2', notes=u'Classification Of Function Of Government, level 2')
    key_cofog3 = model.Key(name=u'cofog3', notes=u'Classification Of Function Of Government, level 3')
    model.Session.add_all([key_cofog1, key_cofog2, key_cofog3])
    key_cofog2.keyvalues[key_parent] = key_cofog1.name
    key_cofog3.keyvalues[key_parent] = key_cofog2.name
    model.Session.commit()
    # For each row in the file...
    reader = csv.reader(fileobj)
    header = reader.next() # Code, Title, Details, Change date.
    for row_index, cells in enumerate(reader):
        code, title, details, change_date = [unicode(x, 'UTF-8') for x in cells]
        # Create the enumeration values.
        print '%r, %r' % (code, title)
        parts = code.split('.')
        parents = [u'.'.join(parts[:i+1]) for i, _ in enumerate(parts)]
        print parents
        if len(parents)==1:
            print 'Creating level 1 code', parents[0]
            ev = model.EnumerationValue(key=key_cofog1, code=parents[0], name=title, notes=details)
            model.Session.add(ev)
        elif len(parents)==2:
            print 'Creating level 2 code', parents[1]
            ev = model.EnumerationValue(key=key_cofog2, code=parents[1], name=title, notes=details)
            ev.keyvalues[key_parent] = parents[0]
            model.Session.add(ev)
        elif len(parents)==3:
            print 'Creating level 3 code', parents[2]
            ev = model.EnumerationValue(key=key_cofog3, code=parents[2], name=title, notes=details)
            ev.keyvalues[key_parent] = parents[1]
            model.Session.add(ev)
        else:
            assert False, code
    model.Session.commit()
    model.Session.remove()

