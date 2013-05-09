# -*- coding: utf-8 -*-
import doctest
from plone.app.testing import (
    applyProfile,
    PLONE_FIXTURE,
    PloneSandboxLayer,
)
from plone.app.testing.layers import (
    FunctionalTesting,
    IntegrationTesting,
)
from Products.CMFCore.utils import getToolByName
from zope.configuration import xmlconfig


class ScBlueprints.soundcloudTesting(PloneSandboxLayer):
    defaultBases = (PLONE_FIXTURE, )

    def setUpZope(self, app, configurationContext):
        # load ZCML
        import sc.blueprints.soundcloud
        xmlconfig.file('configure.zcml', sc.blueprints.soundcloud,
                       context=configurationContext)

    def setUpPloneSite(self, portal):
        # install into the Plone site
        applyProfile(portal, 'sc.blueprints.soundcloud:default')


SCBLUEPRINTS.SOUNDCLOUD_FIXTURE = ScBlueprints.soundcloudTesting()
SCBLUEPRINTS.SOUNDCLOUD_INTEGRATION_TESTING = IntegrationTesting(
    bases=(SCBLUEPRINTS.SOUNDCLOUD_FIXTURE, ),
    name='ScBlueprints.soundcloudLayer:Integration'
)
SCBLUEPRINTS.SOUNDCLOUD_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(SCBLUEPRINTS.SOUNDCLOUD_FIXTURE, ),
    name='ScBlueprints.soundcloudLayer:Functional'
)

optionflags = (doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE)
