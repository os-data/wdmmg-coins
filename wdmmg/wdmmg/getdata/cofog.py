from datetime import date
from zipfile import ZipFile
import csv

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
    import swiss
    cache = swiss.Cache(path='/tmp/')
    filename = cache.retrieve('http://unstats.un.org/unsd/cr/registry/regdntransfer.asp?f=4')
    zipfile = ZipFile(filename, 'r')
    txtfile = zipfile.open('COFOG_english_structure.txt', 'rU')
    headings = txtfile.readline()
    # Semaphore to avoid creating multiple copies.
    assert not model.Session.query(model.Key).filter_by(name=u'cofog1').first()
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
    # Create the enumeration values.
    for line in txtfile.readlines():
        print line
        words = line.split()
        code, description = unicode(words[0]), u' '.join(words[1:])
        parts = code.split('.')
        parents = [u'.'.join(parts[:i+1]) for i, _ in enumerate(parts)]
        print parents
        if len(parents)==1:
            print 'Creating level 1 code', parents[0]
            ev = model.EnumerationValue(key=key_cofog1, name=parents[0], notes=description)
            model.Session.add(ev)
        elif len(parents)==2:
            print 'Creating level 2 code', parents[1]
            ev = model.EnumerationValue(key=key_cofog2, name=parents[1], notes=description)
            ev.keyvalues[key_parent] = parents[0]
            model.Session.add(ev)
        elif len(parents)==3:
            print 'Creating level 3 code', parents[2]
            ev = model.EnumerationValue(key=key_cofog3, name=parents[2], notes=description)
            ev.keyvalues[key_parent] = parents[1]
            model.Session.add(ev)
        else:
            assert False, code
    model.Session.commit()
    model.Session.remove()
    zipfile.close()

