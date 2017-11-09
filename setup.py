"""docknv."""

from setuptools import setup
from docknv.version import __version__

setup(
    name='docknv',
    version=__version__,
    description='Docker with environments',
    url='',
    author='SharingCloud',
    author_email='',
    license='MIT',
    packages=['docknv'],
    install_requires=[
          'six',
          'PyYAML',
          'colorama',
          'Jinja2'
    ],
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'docknv = docknv.shell.main:docknv_entry_point',
        ]
    },
)
