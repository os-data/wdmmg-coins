from setuptools import setup, find_packages

setup(
    name='wdmmg',
    version='0.1',
    description='',
    author='Open Knowledge Foundation',
    author_email='info@okfn.org',
    url='',
    install_requires=[
        "Pylons>=0.9.7,<=0.9.7.99",
        "SQLAlchemy>=0.5,<=0.5.99",
        "Genshi>=0.5,<=0.5.99",
    ],
    setup_requires=["PasteScript>=1.6.3"],
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    test_suite='nose.collector',
    package_data={'wdmmg': ['i18n/*/LC_MESSAGES/*.mo']},
    #message_extractors={'wdmmg': [
    #        ('**.py', 'python', None),
    #        ('public/**', 'ignore', None)]},
    zip_safe=False,
    paster_plugins=['PasteScript', 'Pylons'],
    entry_points="""
    [paste.app_factory]
    main = wdmmg.config.middleware:make_app

    [paste.app_install]
    main = pylons.util:PylonsInstaller

    [paste.paster_command]
    db = wdmmg.lib.cli:ManageDb
    fixtures = wdmmg.lib.cli:Fixtures
    loader = wdmmg.lib.cli:Loader
    """,
)
