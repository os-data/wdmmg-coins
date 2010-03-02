This is the main development repository for `Where Does My Money Go`_

.. _Where Does My Money Go: http://www.wheredoesmymoneygo.org/

It is a mercurial repository and can be found online at:

https://knowledgeforge.net/okfn/wdmmg

Crib sheet
----------

You can get started with the following sequence of commands:

  hg clone https://knowledgeforge.net/okfn/wdmmg

This will download a copy of the repository, and put it inside a newly-created wdmmg directory.

To check-in your changes:

  hg ci
  hg push

To get other people's changes:

  hg pull
  hg up

To avoid typing in your password every time you push, edit the file wdmmg/.hg/hgrc . You should see a line giving the URL from which you cloned the repository. Add your username and password to the line as follows:

  [paths]
  default = https://username:password@knowledgeforge.net/okfn/wdmmg

Rough Guide to the Repository
=============================

/doc/: Documentation, plans, ideas etc

/econdata/: material related to external data including code for scraping,
  cleaning and normalizing that data.

/wdmmg/: the main WDMMG web application (Pylons-based) which provides the store.

License
=======

Copyright (and Database Rights) (c) 2010 the Open Knowledge Foundation,
<info@okfn.org>.

Unless otherwise stated:

  * Any rights in code are licensed under the `GNU Affero GPL`_ v3
  * Any rights in content are licensed under a `Creative Commons Attribution-ShareAlike`_ license (all jurisdictions)
  * Any rights in data(bases) are licensed under a the `Open Data Commons ODbL`_ (Open Database License)

.. _GNU Affero GPL: http://www.fsf.org/licensing/licenses/agpl-3.0.html
.. _Creative Commons Attribution-ShareAlike: http://creativecommons.org/licenses/by-sa/3.0/
.. _Open Data Commons ODbL: http://www.opendatacommons.org/licenses/odbl/1.0/

