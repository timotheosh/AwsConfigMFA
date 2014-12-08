from setuptools import setup, find_packages  # Always prefer setuptools over distutils
from codecs import open  # To use a consistent encoding
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'DESCRIPTION.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='AwsConfigMFA',
    version='0.0.2',
    description='Python module for managing MFA tokens with Amazon Web Services',
    long_description=long_description,
    url='https://github.com/timotheosh/AwsConfigMFA',
    author='Tim Hawes',
    author_email='tim@easyfreeunix.com',
    license='Artistic 2.0',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Artistic License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],
    keywords='Amazon Web Services MFA',
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    install_requires=['boto'],
)
