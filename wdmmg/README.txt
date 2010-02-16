Installation and Setup
======================

Install ``wdmmg`` using easy_install::

    pip -E {your-pyenv} install -e hg+https://knowledgeforge.net/okfn/wdmmg/wdmmg#egg=wdmmg

Make a config file as follows::

    paster make-config wdmmg config.ini

Tweak the config file as appropriate and then setup the application::

    paster setup-app config.ini

Then you are ready to go.
