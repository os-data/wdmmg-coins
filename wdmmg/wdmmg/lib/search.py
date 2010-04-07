from sqlalchemy.sql.expression import and_, or_, func

from wdmmg import model

def account_query(q):
    '''
    Returns an SQLAlchemy query object. Example usage:
    
    for row in account_query(u'work pensions').all():
        print row
    '''
    query = model.Session.query(model.Account)
    for word in q.split():
        query = query.filter(or_(
            func.lower(model.Account.name).contains(word.lower()),
            func.lower(model.Account.notes).contains(word.lower()),
            model.Account.id.startswith(word.lower())
        ))
    return query

