#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ['Click>=8.0.3', 'toml==0.10.2']

test_requirements = ['pytest>=3', ]

setup(
    author="Sekou Diao",
    author_email='diao.sekou.nlp@gmail.com',
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    description="pyprojectify is a utility allowing python package authors/maintainers/packagers to painlessly migrate their package from setup.py to the new pyproject.toml.",
    entry_points={
        'console_scripts': [
            'pyprojectify=pyprojectify.cli:main',
        ],
    },
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='pyprojectify',
    name='pyprojectify',
    packages=find_packages(include=['pyprojectify', 'pyprojectify.*']),
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/SekouDiaoNlp/pyprojectify',
    version='0.2.0',
    zip_safe=False,
)
