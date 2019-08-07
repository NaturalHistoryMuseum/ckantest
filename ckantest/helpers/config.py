#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckantest
# Created by the Natural History Museum in London, UK

from ckan.plugins import toolkit, interfaces
from ckan import plugins


class Configurer(object):
    '''
    A class for easily and consistently accessing, resetting, and otherwise
    manipulating the current config within tests.
    '''

    def __init__(self, app, debug=True):
        self.app = app
        self.debug = debug
        self.stored = None
        self._changed = {}
        self.store()
        self.reset()

    def store(self):
        '''
        Stores a copy of the current config.
        '''
        self.stored = toolkit.config.copy()

    @property
    def current(self):
        '''
        Returns the current config.
        :return: Config
        '''
        return toolkit.config

    def reset(self):
        '''
        Overwrites the current config with the stored config.
        '''
        toolkit.config.update(self.stored)

    def update(self, new_values):
        '''
        Updates the config with the specified values and stores the old
        value of each in case it needs to be reverted to.
        :param new_values: A dictionary of config keys and new values.
        '''
        for key, value in new_values.items():
            if key not in self._changed.keys():
                self._changed[key] = toolkit.config.get(key, None)
            toolkit.config[key] = value

    def remove(self, keys):
        '''
        Removes a list of keys from the config, but stores their old values
        first in case they need to be restored.
        :param keys: A list of keys to be removed from the config.
        '''
        for k in keys:
            if k not in self._changed.keys():
                self._changed[k] = toolkit.config.get(k, None)
            if k in toolkit.config.keys():
                del toolkit.config[k]

    def undo(self, key):
        '''
        Restore the old value of a single key. If it wasn't in the config to
        start with or it was never changed, it is deleted.
        :param key: The key to revert.
        '''
        if key in self._changed.keys() and self._changed.get(key, None):
            toolkit.config[key] = self._changed[key]
        else:
            del toolkit.config[key]
        del self._changed[key]

    def load_plugins(self, *plugin_names):
        for p in plugin_names:
            plugins.load(p)
            plugin = plugins.get_plugin(p)
            if not hasattr(plugin, u'get_blueprint'):
                continue
            for blueprint in plugin.get_blueprint():
                self.app.flask_app.register_extension_blueprint(blueprint)
