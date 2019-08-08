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
        cls.app = helpers._get_test_app()
        cls.config = ckantest.helpers.Configurer(cls.app, cls.persist)
        cls.config.load_plugins(*cls.plugins)
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
            cls._df = ckantest.factories.DataFactory()
        return cls._df
