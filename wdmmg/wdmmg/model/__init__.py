"""The application's model objects"""
import sqlalchemy as sa
from sqlalchemy import orm

from wdmmg.model import meta
from meta import Session
from atp import Slice, Account, Transaction, Posting
from keyvalue import Key, EnumerationValue, KeyValue, add_keyvalues
add_keyvalues(Account)
add_keyvalues(Transaction)
add_keyvalues(Posting)

def init_model(engine):
    '''Call me before using any of the tables or classes in the model'''
    meta.Session.configure(bind=engine)
    meta.engine = engine


class Repository(object):
    def create_db(self):
        meta.metadata.create_all()
    
    def init_db(self):
        pass
    
    def clean_db(self):
        meta.metadata.drop_all()

    def rebuild_db(self):
        self.clean_db()
        self.create_db()
    
    def delete_all(self):
        for obj in [ Posting, Transaction, Account, Slice, KeyValue, Key, 
            EnumerationValue]:
            Session.query(obj).delete()
        Session.commit()
        Session.remove()



repo = Repository()

