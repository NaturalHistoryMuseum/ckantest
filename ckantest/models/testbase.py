#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckantest
# Created by the Natural History Museum in London, UK

import ckantest.factories
import ckantest.helpers

from ckan.tests import helpers
from unittest import TestCase


class TestBase(TestCase):
    '''

    '''
    plugins = []  # a list of plugin names to load
    persist = {}  # config settings to maintain when resetting, e.g. {'myextension.debug': True}

    @classmethod
    def setup_class(cls):
        cls.config = ckantest.helpers.Configurer(cls.persist)
        cls.config.load_plugins(*cls.plugins)
        cls.app = helpers._get_test_app()
        cls.config.register_blueprints(cls.app)
        cls.context = cls.app.flask_app.test_request_context()
        cls._session = ckantest.helpers.mocking.session()
        cls._df = None

    @classmethod
    def teardown_class(cls):
        cls.config.reset()
        if cls._df is None:
            helpers.reset_db()
        else:
            cls.data_factory().destroy()

    @classmethod
    def data_factory(cls):
        if cls._df is None:
            with cls.context:
                cls._df = ckantest.factories.DataFactory()
        return cls._df

    def api_request(self, action, params=None, method='get'):
        '''Helper method to submit a request to the API.

        :param action: the name of the api action to be called, e.g. package_create
        :type action: str
        :param params: additional parameters to submit
        :type params: dict

        '''

        url = str('/api/3/action/{0}'.format(action))

        try:
            _request = getattr(self.app, method.lower())
        except AttributeError:
            _request = self.app.get

        response = _request(url, params=params, headers={
            'Authorization': str(self.data_factory().sysadmin[u'apikey'])
            })
        return response.json
