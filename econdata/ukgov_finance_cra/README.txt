Extract, clean and analyse UK Gov Country and Regional Analyses (CRA).

This is being distributed as a python package. To get going::

    # make sure you are in this directory
    cd ....
    # set up a virtualenv for any dependencies
    virtualenv pyenv
    # install using pip
    pip -E pyenv install -e .
    # now try it out
    python data.py -h

NB: the database stuff (db.py) requires SQLAlchemy.

