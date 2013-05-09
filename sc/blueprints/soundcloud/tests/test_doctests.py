# -*- coding: utf-8 -*-
import doctest
import unittest2 as unittest
from plone.testing import layered
from sc.blueprints.soundcloud.testing import (
    SCBLUEPRINTS.SOUNDCLOUD_FUNCTIONAL_TESTING,
    optionflags,
)

functional_tests = [
    # add here the functional doctest file names
]


def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([
        layered(doctest.DocFileSuite('tests/%s' % test_file,
                                     package='scblueprints.soundcloud',
                                     optionflags=optionflags),
                layer=SCBLUEPRINTS.SOUNDCLOUD_FUNCTIONAL_TESTING)
        for test_file in functional_tests
        ])
    return suite
