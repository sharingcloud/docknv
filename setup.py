"""docknv."""

from setuptools import setup
from docknv.version import __version__

setup(
    name='docknv',
    version=__version__,
    description='Docker with environments',
    url='https://bitbucket.org/sharingcloud/docknv',
    author='Denis BOURGE',
    author_email='denis.bourge@sharingcloud.com',
    license='MIT',
    packages=['docknv'],
    install_requires=[
          'six',
          'PyYAML',
          'colorama',
          'Jinja2',
          'whichcraft',
          'docker',
          'pypiwin32'
    ],
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'docknv = docknv.shell.main:docknv_entry_point',
        ]
    },
)
