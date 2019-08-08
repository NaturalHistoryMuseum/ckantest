#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckantest
# Created by the Natural History Museum in London, UK


from ckan import __version__ as ckan_version

from ckan.plugins import toolkit


def resource_read(package, resource):
    kwargs = {
        u'id': package[u'name'],
        u'resource_id': resource[u'id']
        }
    if int(ckan_version[2]) > 8:
        args = [u'resource.read']
    else:
        args = []
        kwargs.update({
            u'controller': u'package',
            u'action': u'resource_read'
            })
    return toolkit.url_for(*args, **kwargs)
