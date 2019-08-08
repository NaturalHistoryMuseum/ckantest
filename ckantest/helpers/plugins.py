#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckantest
# Created by the Natural History Museum in London, UK

from ckan import plugins


def load_datastore():
    try:
        plugins.load(u'datastore')
        return u'datastore'
    except:
        plugins.unload(u'datastore')
        plugins.load(u'versioned_datastore')
        return u'versioned_datastore'


def unload_datastore():
    if plugins.plugin_loaded(u'datastore'):
        plugins.unload(u'datastore')
    if plugins.plugin_loaded(u'versioned_datastore'):
        plugins.unload(u'versioned_datastore')
