#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckantest
# Created by the Natural History Museum in London, UK

from ckantest.helpers import mocking
from ckantest.helpers.containers import Packages

from ckan.plugins import toolkit
from ckan.tests import factories, helpers


class DataFactory(object):
    '''
    A helper class for creating and manipulating standard test datasets.
    '''

    def __init__(self):
        self.sysadmin = None
        self.org = None
        self.users = {}
        self.orgs = {}
        self.packages = Packages()
        self.refresh()

    def package(self, name=None, context=None, **kwargs):
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
            package = factories.Dataset(**data_dict)
        else:
            package = toolkit.get_action(u'package_create')(context, data_dict)
        self.packages[name] = package
        self.activate_package(package[u'id'], context=context)
        return package

    def resource(self, package_id, context=None, **kwargs):
        data_dict = {
            u'package_id': package_id,
            u'url': u'http://placekitten.com/200/300'
            }
        data_dict.update(kwargs)
        if context is None:
            resource = factories.Resource(**data_dict)
        else:
            resource = toolkit.get_action(u'resource_create')(context, data_dict)

        self.activate_package(package_id, context=context)
        data_dict = {
            u'resource_id': resource[u'id'],
            u'force': True
            }
        toolkit.get_action(u'datastore_create')(context or self.context, data_dict)
        data_dict[u'replace'] = True
        with mocking.Patches.sync_queue():
            toolkit.get_action(u'datastore_upsert')(context or self.context, data_dict)
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
        toolkit.get_action(u'package_update')(context or self.context, pkg_dict)

    def activate_package(self, package_id, context=None):
        '''
        Sets a package's state to 'active'.
        :param package_id: The package to activate.
        '''
        pkg_dict = toolkit.get_action(u'package_show')(context or self.context, {
            u'id': package_id
            })
        pkg_dict[u'state'] = u'active'
        toolkit.get_action(u'package_update')(context or self.context, pkg_dict)

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
        Runs all the creation functions in the class, e.g. creating a test
        org and test datasets.
        '''
        self.sysadmin = factories.Sysadmin()
        self.org = factories.Organization()

    def destroy(self):
        '''
        Resets the database and any class variables that have been altered,
        e.g. title string.
        '''
        helpers.reset_db()
        self.sysadmin = None
        self.org = None
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
