from setuptools import setup, find_packages

setup(
    name='ukgov_finances_cra',
    version='0.1',
    # Suitable open licenses can be found at http://www.opendefinition.org/licenses/
    license='PDDL',
    description='Country and Regional Analyses (CRA) - UK Government Finances',
    url='http://www.hm-treasury.gov.uk/pesp_cra.htm',
    download_url='http://www.hm-treasury.gov.uk/d/cra_2009_db.xls',
    keywords='ukgov, country-uk, gov, size-medium, format-csv, format-xls',
    long_description='''

    ''',
    author='UK Government (HMT)',
    maintainer='Rufus Pollock',

    install_requires=[
        'swiss>=0.2',
        ],
    package_dir={'ukgov_finances_cra': ''},
    packages=find_packages(),
    include_package_data=True,
    # do not zip up the package into an 'Egg'
    zip_safe=False,
)
