#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckantest
# Created by the Natural History Museum in London, UK

import logging

from ckantest.helpers import mocking
from ckantest.helpers.containers import Packages

from ckan.plugins import toolkit
from ckan.tests import factories, helpers

logger = logging.getLogger(u'ckantest')


class DataFactory(object):
    '''
    A helper class for creating and manipulating standard test datasets.
    '''

    def __init__(self):
        # defining attribute names
        self._sysadmin = None
        self._org = None
        self.users = None
        self.orgs = None
        self.packages = None
        # this actually sets them properly (so they can be reset as needed)
        self.refresh()

    def package(self, name=None, context=None, activate=True, **kwargs):
        if name is None:
            previous = [int(n.split(u'_')[-1]) for n in self.packages.keys() if
                        n.startswith(u'test_package_')]
            i = max(previous) + 1 if len(previous) > 0 else 1
            name = u'test_package_' + str(i).zfill(3)
        if name in self.packages:
            raise KeyError(u'Duplicated key: ' + name)
        data_dict = {
            u'title': DataConstants.title_short,
            u'name': name,
            u'notes': u'these are some notes',
            u'dataset_category': u'cat1',
            u'private': False,
            u'owner_org': self.org[u'id'],
            u'author': DataConstants.authors_short
            }
        data_dict.update(kwargs)
        if context is None:
            logger.debug(u'Creating dataset "{0}" as sysadmin...'.format(name))
            package = factories.Dataset(**data_dict)
        else:
            logger.debug(u'Creating dataset "{0}" as user {1}...'.format(name, context[u'user']))
            package = toolkit.get_action(u'package_create')(context, data_dict)
        self.packages[name] = package
        if activate:
            self.activate_package(package[u'id'], context=context)
        return package

    def resource(self, package_id, context=None, records=None, activate=True, **kwargs):
        data_dict = {
            u'package_id': package_id,
            u'url': u'http://placekitten.com/200/300'
            }
        data_dict.update(kwargs)
        if context is None:
            logger.debug(u'Creating resource as sysadmin...')
            resource = factories.Resource(**data_dict)
        else:
            logger.debug(u'Creating resource as user {0}...'.format(context[u'user']))
            resource = toolkit.get_action(u'resource_create')(context, data_dict)

        if activate:
            self.activate_package(package_id, context=context)
            data_dict = {
                u'resource_id': resource[u'id'],
                u'force': True
                }
            if records:
                data_dict[u'records'] = records
            use_context = context or self.context
            logger.debug(u'Adding resource to datastore as user {0}...'.format(use_context[u'user']))
            toolkit.get_action(u'datastore_create')(use_context, data_dict)
            data_dict[u'replace'] = True
            with mocking.Patches.sync_queue():
                toolkit.get_action(u'datastore_upsert')(use_context, data_dict)
        return resource

    def organisation(self, name=None, **kwargs):
        if name is None:
            name = u'test_org_' + str(
                max([int(n.split(u'_')[-1]) for n in self.orgs.keys()]) + 1).zfill(3)
        if name in self.orgs:
            raise KeyError(u'Duplicated key: ' + name)
        data_dict = {
            u'name': name,
            }
        data_dict.update(kwargs)
        logger.debug(u'Creating organisation "{0}" as sysadmin...'.format(name))
        org = factories.Organization(**data_dict)
        self.orgs[name] = org
        return org

    def user(self, name=None, **kwargs):
        if name is None:
            name = u'test_user_' + str(
                max([int(n.split(u'_')[-1]) for n in self.users.keys()]) + 1).zfill(3)
        if name in self.users:
            raise KeyError(u'Duplicated key: ' + name)
        data_dict = {
            u'name': name
            }
        data_dict.update(kwargs)
        logger.debug(u'Creating user "{0}" as sysadmin...'.format(name))
        user = factories.User(**data_dict)
        self.users[name] = user
        return user

    def deactivate_package(self, package_id, context=None):
        '''
        Sets a package's state to 'inactive'.
        :param package_id: The package to deactivate.
        '''
        pkg_dict = toolkit.get_action(u'package_show')(context or self.context, {
            u'id': package_id
            })
        pkg_dict[u'state'] = u'inactive'
        use_context = context or self.context
        logger.debug(u'Deactivating package {0} as user {1}...'.format(pkg_dict[u'name'],
                                                                       use_context[u'user']))
        toolkit.get_action(u'package_update')(use_context, pkg_dict)

    def activate_package(self, package_id, context=None):
        '''
        Sets a package's state to 'active'.
        :param package_id: The package to activate.
        '''
        pkg_dict = toolkit.get_action(u'package_show')(context or self.context, {
            u'id': package_id
            })
        pkg_dict[u'state'] = u'active'
        use_context = context or self.context
        logger.debug(u'Activating package {0} as user {1}...'.format(pkg_dict[u'name'],
                                                                     use_context[u'user']))
        toolkit.get_action(u'package_update')(use_context, pkg_dict)

    def remove_resources(self, package_name, context=None):
        '''
        Delete all resources from the specified package.
        '''
        for r in self.packages[package_name].get(u'resources', []):
            toolkit.get_action(u'resource_delete')(context or self.context, {
                u'id': r[u'id']
                })
        self.packages[package_name] = toolkit.get_action(u'package_show')(context or self.context, {
            u'id': self.packages[package_name][u'id']
            })

    def deactivate_resources(self, package_name):
        '''
        Does not make any actual database changes - makes a copy of the
        current specified package dictionary and mocks deactivating all
        its resources by setting their states to 'draft'. Returns this mock
        dictionary.
        :return: dict
        '''
        pkg_dict = self.packages[package_name].copy()
        resources_dict = pkg_dict[u'resources']
        for r in resources_dict:
            r[u'state'] = u'draft'
        pkg_dict[u'resources'] = resources_dict
        return pkg_dict

    def create(self):
        '''
        Runs any necessary creation functions.
        '''

    def destroy(self):
        '''
        Resets the database and any class variables that have been altered,
        e.g. title string.
        '''
        helpers.reset_db()
        self._sysadmin = None
        self._org = None
        self.users = {}
        self.orgs = {}
        self.packages = Packages()

    def refresh(self):
        '''
        Resets and recreates the data. Mostly for convenience.
        '''
        self.destroy()
        self.create()

    @property
    def context(self):
        '''
        Defines a context to operate in, using the sysadmin user. Defined as
        a property to work around an authentication issue in ckanext-harvest.
        :return: dict
        '''
        context = {
            u'user': self.sysadmin[u'name'],
            u'ignore_auth': True
            }
        # to fix an issue in ckanext-harvest (commit f315f41)
        context.pop(u'__auth_audit', None)
        return context

    @property
    def sysadmin(self):
        if self._sysadmin is None:
            self._sysadmin = factories.Sysadmin()
        return self._sysadmin

    @property
    def org(self):
        if self._org is None:
            self._org = factories.Organization()
        return self._org


class DataConstants(object):
    title_long = u'This is a very long package title that is going to be approximately ' \
                 u'two hundred characters long by the time it is finished. It is being ' \
                 u'used to test extensions for CKAN as part of the ckantest package.'
    title_short = u'A test package'

    authors_long = u'Waylon Dalton; Justine Henderson; ' \
                   u'Abdullah Lang; Marcus Cruz; Thalia Cobb; ' \
                   u'Mathias Little; Eddie Randolph; ' \
                   u'Angela Walker; Lia Shelton; Hadassah Hartman; ' \
                   u'Joanna Shaffer; Jonathon Sheppard'
    authors_long_first = u'Dalton'
    authors_short = u'Test Author'
    authors_short_first = u'Author'

    records = [{
        u'common_name': u'Egyptian vulture',
        u'scientific_name': u'Neophron percnopterus'
        }, {
        u'common_name': u'Malabar squirrel',
        u'scientific_name': u'Ratufa indica'
        }, {
        u'common_name': u'Screamer, crested',
        u'scientific_name': u'Chauna torquata'
        }, {
        u'common_name': u'Heron, giant',
        u'scientific_name': u'Ardea golieth'
        }, {
        u'common_name': u'Water monitor',
        u'scientific_name': u'Varanus salvator'
        }]
