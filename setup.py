from __future__ import with_statement

from setuptools import setup


def get_version():
    from aheui import version
    return version.VERSION


def get_readme():
    try:
        with open('README.md') as f:
            return f.read().strip()
    except IOError:
        return ''


tests_require = [
    'ruff', 'tox', 'pytest>=3.0.1',
]

setup(
    name='aheui',
    version=get_version(),
    description='Aheui compiler & assembler toolkit.',
    long_description=get_readme(),
    long_description_content_type='text/markdown',
    author='Jeong YunWon',
    author_email='aheui@youknowone.org',
    url='https://github.com/aheui/rpaheui',
    packages=[
        'aheui',
        'aheui/int',
    ],
    package_data={
        'aheui': ['version.py']
    },
    install_requires=[
    ],
    tests_require=tests_require,
    extras_require={
        'tests': tests_require,
    },
    scripts=[
        'bin/aheui-py',
        'bin/aheui',
        'bin/ahsembler',
    ],
    classifiers=[
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.12',
    ],
)
