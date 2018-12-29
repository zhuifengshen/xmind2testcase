#!/usr/env/bin python
# -*- coding: utf-8 -*-
import io
import os
import sys
from shutil import rmtree
from setuptools import setup, find_packages, Command

about = {}
here = os.path.abspath(os.path.dirname(__file__))
with io.open(os.path.join(here, 'xmind2testcase', '__about__.py'), encoding='utf-8') as f:  # custom
    exec(f.read(), about)

with io.open('README.md', encoding='utf-8') as f:
    long_description = f.read()

install_requires = [  # custom
    "xmind",
    "flask",
    "arrow",
]


class PyPiCommand(Command):
    """ Build and publish this package and make a tag.
        Support: python setup.py pypi
        Copied from requests_html
    """
    user_options = []

    @staticmethod
    def status(s):
        """Prints things in green color."""
        print('\033[0;32m{0}\033[0m'.format(s))

    def initialize_options(self):
        """ override
        """
        pass

    def finalize_options(self):
        """ override
        """
        pass

    def run(self):
        self.status('Building Source and Wheel (universal) distribution...')
        os.system('{0} setup.py sdist bdist_wheel --universal'.format(sys.executable))

        self.status('Uploading the package to PyPi via Twine...')
        os.system('twine upload dist/*')

        self.status('Publishing git tags...')
        os.system('git tag v{0}'.format(about['__version__']))
        os.system('git push --tags')

        try:
            self.status('Removing current build artifacts...')
            rmtree(os.path.join(here, 'dist'))
            rmtree(os.path.join(here, 'build'))
            rmtree(os.path.join(here, 'xmind2testcase.egg-info'))  # custom
        except OSError:
            pass

        self.status('Congratulations! Upload PyPi and publish git tag successfully...')
        sys.exit()


setup(
    name=about['__title__'],
    version=about['__version__'],
    description=about['__description__'],
    long_description=long_description,
    long_description_content_type='text/markdown',
    keywords=about['__keywords__'],
    author=about['__author__'],
    author_email=about['__author_email__'],
    url=about['__url__'],
    license=about['__license__'],
    packages=find_packages(exclude=['tests', 'test.*', 'docs']),  # custom
    package_data={  # custom
        '': ['README.md'],
        'webtool': ['static/*', 'static/css/*', 'static/guide/*', 'templates/*', 'schema.sql'],
    },
    install_requires=install_requires,
    extras_require={},
    python_requires='>=3.0, <4',  # custom
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={  # custom
        'console_scripts': [
            'xmind2testcase=xmind2testcase.cli:cli_main',
        ]
    },
    cmdclass={
        # python3 setup.py pypi
        'pypi': PyPiCommand
    }
)
