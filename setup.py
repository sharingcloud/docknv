from setuptools import setup

setup(
    name='docknv',
    version='1.0',
    description='Configurable Docker Compose',
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
    #scripts=['bin/docknv'],
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'docknv = docknv.shell:docknv_entry_point',
        ]
    },
)
