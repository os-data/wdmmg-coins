import logging
from datetime import date
from zipfile import ZipFile
from StringIO import StringIO
import os, csv

import datapkg
from swiss.tabular import gdocs
from pylons import config
from ordf.changeset import ChangeSet
from ordf.graph import Graph
from ordf.namespace import namespaces, Namespace, DC, RDF, FOAF, OWL, RDFS, SKOS
from ordf.term import URIRef

log = logging.getLogger(__name__)

import wdmmgrdf.model as model

def load():
    '''Downloads the COFOG list, and loads it into the database with key names
    'cofog1', 'cofog2' and 'cofog3'.
    '''
    # Get the COFOG data package.
    pkgspec = 'file://%s' % os.path.join(config['getdata_cache'], 'cofog')
    pkg = datapkg.load_package(pkgspec)
    fileobj = pkg.stream('cofog.n3')
    load_file(fileobj)

COFOG_IDENTIFIER = URIRef('http://cofog.eu/cofog/1999')

def load_file(fileobj):
    '''Loads the specified COFOG-like file into the database with key names
    'cofog1', 'cofog2' and 'cofog3'.
    '''
    # TODO: replace with simple import of the cofog rdf data which already has
    # relevant structure
    from wdmmgrdf.model import handler
    ctx = handler.context(u'importer', u'loading cofog')
    g = Graph(identifier=COFOG_IDENTIFIER)
    g.parse(fileobj, format='n3')
    log.info('add %s' % g.identifier)
    ctx.add(g)
    log.info('commit changes')
    cs = ctx.commit()


def dejargonise():
    '''Downloads alternative names for the COFOG codes, chosen specially for WDMMG,
    and replaces the names in the database.
    
    The original names are backed up.
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

def promote_notes():
    '''Where a level 2 COFOG code has exactly one level 3 sub-code, there is
    often no detailed description for the level 2 code and this method will
    supply the missing description by copying it from the level 3 sub-code.
    '''
    key_cofog2 = model.Session.query(model.Key).filter_by(name=u'cofog2').one()
    key_cofog3 = model.Session.query(model.Key).filter_by(name=u'cofog3').one()
    key_parent = model.Session.query(model.Key).filter_by(name=u'parent').one()
    all_cofog2s = (model.Session.query(model.EnumerationValue)
        .filter_by(key=key_cofog2)
        ).all()
    for ev in all_cofog2s:
        if ev.notes:
            continue
        children = (model.Session.query(model.EnumerationValue)
            .filter_by(key=key_cofog3)
            .join((model.KeyValue, model.KeyValue.object_id==model.EnumerationValue.id))
            .filter(model.KeyValue.key == key_parent)
            .filter(model.KeyValue.value == ev.code)
            ).all()
        if len(children)==1 and children[0].notes:
            # Copy `notes` from child to parent.
            print "Copying notes from %s to %s" % (children[0].code, ev.code)
            print "Old notes = ", ev.notes
            ev.notes = children[0].notes
            print "New notes = ", ev.notes
    model.Session.commit()
    model.Session.remove()
