#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckantest
# Created by the Natural History Museum in London, UK

from ckan.plugins import toolkit


class DictWrapper(object):
    '''
    Wraps a dict so that the __getitem__ method can be overridden.
    '''
    def __init__(self):
        self._dict = {}

    def keys(self):
        return self._dict.keys()

    def items(self):
        return [(k, self._dict.get(k)) for k in self._dict.keys()]

    def values(self):
        return [self._dict.get(k) for k in self._dict.keys()]

    def get(self, item, default_value=None):
        return self._dict.get(item, default_value)

    def __getitem__(self, item):
        return self.get(item)

    def __setitem__(self, key, value):
        self._dict[key] = value

    def __contains__(self, item):
        return item in self._dict


class Packages(DictWrapper):
    def get(self, item, default_value=None):
        pkg_dict = super(Packages, self).get(item, None)
        if pkg_dict is None:
            return default_value
        package_id = pkg_dict[u'id']
        return toolkit.get_action(u'package_show')({u'ignore_auth': True}, {
            u'id': package_id
            })
