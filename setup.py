# -*- coding: utf-8 -*-
from setuptools import setup, find_packages


version = "0.1"
description = "Transmogrifier blueprints to upload/use content from soundcloud.com"
long_description = open("README.rst").read() + open("HISTORY.rst").read() + \
    open("LICENSE").read()


setup(
    name="sc.blueprints.soundcloud",
    version=version,
    description=description,
    long_description=long_description,
    classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
    ],
    author=u"João S. O. Bueno",
    author_email="jsbueno@simplesconsultoria.com.br",
    url="https://github.com/plone/sc.blueprints.soundcloud",
    license="GPL",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    namespace_packages=["sc", "sc.blueprints"],
    # This does not require collective.transmogrifier -
    # but it is needded to actually runt he blueprints
    install_requires=[
        "setuptools",
        "Products.CMFPlone",
        "five.grok",
        "plone.app.dexterity",
        "requests",
        "sc.transmogrifier",
        "soundcloud",
        "z3c.jbot"
    ],
    extras_require={
        "test": [
            "plone.app.testing",
        ]
    },
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """,
)
