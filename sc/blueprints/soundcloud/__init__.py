# -*- coding: utf-8 -*-
from zope.i18nmessageid import MessageFactory
import logging

logger = logging.getLogger("SC Blueprints Soundcloud")


DOMAIN = u'sc.blueprints.soundcloud'
_ = MessageFactory(DOMAIN)
