#!/usr/bin/env python3
# -*- coding:utf-8 -*-

""" Setup for SAML App Configuration CloudFormation Stack Deployment App

The setup script defines the modules required to build this app
"""

import setuptools

with open("README.md") as fp:
    long_description = fp.read()

requirements = [
    "boto3",
    "argparse",
    "cfn_flip",
    "awsume"
]

dev_requirements = [
    "autopep8",
    "pylint",
    "pytest",
    "pytest-dotenv",
    "pytest-cov"
]

setuptools.setup(
    name="saml-app-config-cfn",
    version="0.0.1",

    description="SAML App Configuration CloudFormation Stack Deployment",
    long_description=long_description,
    long_description_content_type="text/markdown",

    author="Charlene Leong",

    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),

    install_requires=requirements,
    extras_require={"dev": dev_requirements},

    python_requires=">=3.7.5",

    classifiers=[
        "Development Status :: Development",

        "Intended Audience :: Deloitte Cloud Engineering Operate",

        "Programming Language :: Python :: 3.7.5",

        "Topic :: Utilities",

        "Typing :: Typed",
    ],
)

