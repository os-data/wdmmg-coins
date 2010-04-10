import os
import sys

import paste.script.command

class WdmmgCommand(paste.script.command.Command):
    parser = paste.script.command.Command.standard_parser(verbose=True)
    parser.add_option('-c', '--config', dest='config',
            default='development.ini', help='Config file to use (default: development.ini)')
    default_verbosity = 1
    group_name = 'wdmmg'

    def _load_config(self):
        from paste.deploy import appconfig
        from wdmmg.config.environment import load_environment
        if not self.options.config:
            msg = 'No config file supplied'
            raise self.BadCommand(msg)
        self.filename = os.path.abspath(self.options.config)
        conf = appconfig('config:' + self.filename)
        load_environment(conf.global_conf, conf.local_conf)

    def _setup_app(self):
        cmd = paste.script.appinstall.SetupCommand('setup-app') 
        cmd.run([self.filename]) 


class ManageDb(WdmmgCommand):
    '''Perform various tasks on the database.
    
    db create # create
    db init # create and put in default data
    db clean
    # db upgrade [{version no.}] # Data migrate
    '''
    summary = __doc__.split('\n')[0]
    usage = __doc__
    max_args = None
    min_args = 1

    def command(self):
        self._load_config()
        from wdmmg import model

        cmd = self.args[0]
        if cmd == 'create':
            model.repo.create_db()
        elif cmd == 'init':
            model.repo.init_db()
        elif cmd == 'clean' or cmd == 'drop':
            model.repo.clean_db()
        elif cmd == 'upgrade':
            if len(self.args) > 1:
                model.repo.upgrade_db(self.args[1])
            else:
                model.repo.upgrade_db()
        else:
            print 'Command %s not recognized' % cmd
            sys.exit(1)


class Fixtures(WdmmgCommand):
    '''Setup (and teardown) fixtures.

        setup: setup fixtures
        teardown: teardown fixtures
    
    '''
    summary = __doc__.split('\n')[0]
    usage = __doc__
    max_args = None
    min_args = 1

    def command(self):
        self._load_config()
        cmd = self.args[0]
        if cmd == 'setup':
            self.setup()
        elif cmd == 'teardown':
            self.teardown()

    @classmethod
    def setup(self):
        from wdmmg import model
        import pkg_resources
        from wdmmg.getdata.cra import CRALoader
        model.repo.delete_all()
        model.Session.remove()
        fileobj = pkg_resources.resource_stream('wdmmg', 'tests/cra_2009_db_short.csv')
        CRALoader.load(fileobj)
        model.Session.commit()
        model.Session.remove()
        self.slice_ = (model.Session.query(model.Slice)
            .filter_by(name=CRALoader.slice_name)
            ).one()
        self.govt_account = (model.Session.query(model.Account)
            .filter_by(name=CRALoader.govt_account_name)
            ).one()
        self.spender = model.Session.query(model.Key).filter_by(name=u'spender').one()
        self.dept = model.Session.query(model.Key).filter_by(name=u'dept').one()
        self.pog = model.Session.query(model.Key).filter_by(name=u'pog').one()
        self.cofog = model.Session.query(model.Key).filter_by(name=u'function').one()
        self.region = model.Session.query(model.Key).filter_by(name=u'region').one()
    
    @classmethod
    def teardown(self):
        from wdmmg import model
        model.repo.delete_all()
        model.Session.remove()

