#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckantest
# Created by the Natural History Museum in London, UK

import logging

from ckan import plugins

logger = logging.getLogger(u'ckantest')


def load_datastore():
    try:
        plugins.load(u'datastore')
        logger.debug(u'Loaded datastore.')
        return u'datastore'
    except Exception as e:
        logger.debug(u'Couldn\'t load datastore: ' + str(e))
        plugins.unload(u'datastore')
        plugins.load(u'versioned_datastore')
        logger.debug(u'Loaded versioned datastore.')
        return u'versioned_datastore'


def unload_datastore():
    if plugins.plugin_loaded(u'datastore'):
        plugins.unload(u'datastore')
    if plugins.plugin_loaded(u'versioned_datastore'):
        plugins.unload(u'versioned_datastore')
