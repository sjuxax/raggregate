import os
import sys

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README')).read()
CHANGES = open(os.path.join(here, 'CHANGELOG')).read()

requires = [
    'pyramid>=1.3a1',
    'SQLAlchemy',
    'transaction',
    'repoze.tm2>=1.0b1', # default_commit_veto
    'zope.sqlalchemy',
    'WebError',
    'cryptacular',
    'pyramid_beaker',
    'sqlahelper',
    'python-memcached',
    'sunburnt',
    'httplib2',
    'lxml',
    'twython',
    'pillow',
    'pytz',
    'pyramid-tm',
    'Markdown',
    'sjuxax-facebook',
    'slugify',
    'nose',
    'coverage',
    ]

if sys.version_info[:3] < (2,5,0):
    requires.append('pysqlite')

setup(name='raggregate',
      version='0.0',
      description='raggregate',
      long_description=README + '\n\n' +  CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pylons",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='',
      author_email='',
      url='',
      keywords='web wsgi bfg pylons pyramid',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='raggregate',
      install_requires = requires,
      entry_points = """\
      [paste.app_factory]
      main = raggregate:main
      """,
      paster_plugins=['pyramid'],
      dependency_links=['http://github.com/sjuxax/python-sdk/tarball/master#egg=sjuxax-facebook']
      )

