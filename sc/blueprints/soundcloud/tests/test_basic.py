# -*- coding: utf-8 -*-
import unittest2 as unittest

from Products.CMFCore.utils import getToolByName

from sc.blueprints.soundcloud.testing import (
    SCBLUEPRINTS.SOUNDCLOUD_INTEGRATION_TESTING,
)


class TestExample(unittest.TestCase):

    layer = SCBLUEPRINTS.SOUNDCLOUD_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.qi_tool = getToolByName(self.portal, 'portal_quickinstaller')

    def test_product_is_installed(self):
        """ Validate that sc.blueprints.soundcloud has been installed
        """
        pid = 'sc.blueprints.soundcloud'
        installed = [p['id'] for p in self.qi_tool.listInstalledProducts()]
        self.assertTrue(pid in installed,
                        'sc.blueprints.soundcloud appears not to have been installed')
