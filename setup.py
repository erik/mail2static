from setuptools import setup, find_packages

__version__ = '1.2.0'


setup(
    name='mail2static',
    version=__version__,
    description='',
    long_description='',
    author='Erik Price',
    url='https://github.com/erik/mail2static',
    packages=find_packages(),
    python_requires='>=3.5',
    license='AGPLv3+',
    install_requires=[
        'flask==1.0.2',
        'toml==0.10.0',
        'attrs==18.2.0',
    ],
    classifiers=[
    ]
)
