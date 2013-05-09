# -*- coding: utf-8 -*-
import logging


# define here the methods needed to be run at install time


def importVarious(context):
    if context.readDataFile('sc.blueprints.soundcloud_various.txt') is None:
        return
    logger = logging.getLogger('sc.blueprints.soundcloud')

    # add here your custom methods that need to be run when
    # sc.blueprints.soundcloud is installed
