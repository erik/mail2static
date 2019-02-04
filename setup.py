import os.path

from setuptools import setup, find_packages

__version__ = '1.2.0'


setup(
    name='mail2jekyll',
    version=__version__,
    description='',
    long_description='',
    author='Erik Price',
    url='https://github.com/erik/mail2jekyll',
    packages=find_packages(),
    python_requires='>=3.5',
    license='AGPLv3+',
    install_requires=[
        'flask==1.0.2',
        'toml==0.10.0',
    ],
    classifiers=[
    ]
)
