"""Pylons environment configuration"""
import os

from genshi.template import TemplateLoader
from pylons import config
from ordf.handler import init_handler

import wdmmgrdf.lib.app_globals as app_globals
import wdmmgrdf.lib.helpers
from wdmmgrdf.config.routing import make_map
import wdmmgrdf.model as model

def load_environment(global_conf, app_conf):
    """Configure the Pylons environment via the ``pylons.config``
    object
    """
    # Pylons paths
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    paths = dict(root=root,
                 controllers=os.path.join(root, 'controllers'),
                 static_files=os.path.join(root, 'public'),
                 templates=[os.path.join(root, 'templates')])

    # Initialize config with the basic options
    config.init_app(global_conf, app_conf, package='wdmmgrdf', paths=paths)

    config['routes.map'] = make_map()
    config['pylons.app_globals'] = app_globals.Globals()
    config['pylons.h'] = wdmmgrdf.lib.helpers

    # Create the Genshi TemplateLoader
    config['pylons.app_globals'].genshi_loader = TemplateLoader(
        paths['templates'], auto_reload=True)

    # CONFIGURATION OPTIONS HERE (note: all config options will override
    # any Pylons config options)

    model.handler = init_handler(config)

