#!/usr/bin/env python

from setuptools import setup, find_packages
import django_kms

setup(
    name='django-kms-field',
    version=django_kms.__version__,
    description='Add Amazon KMS encrypted database fields',
    long_description=open('README.md').read(),
    author='Shaun Kruger',
    author_email='shaun.kruger@gmail.com',
    url = 'https://github.com/skruger/django-kms-field',
    packages= find_packages(exclude=('tests*',)),
    license='The MIT License: http://www.opensource.org/licenses/mit-license.php',
    platforms='all',
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ],
    install_requires=[
        "boto3>=1.13",
    ],
    include_package_data=True,
    zip_safe=False,
)
