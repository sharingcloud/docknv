"""
Docknv
"""

__version__ = ""

from setuptools import setup
execfile('docknv/version.py')

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
    scripts=['bin/docknv'],
    zip_safe=False
)
