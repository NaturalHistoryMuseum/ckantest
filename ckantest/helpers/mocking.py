#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckantest
# Created by the Natural History Museum in London, UK

import beaker

import mock


def session():
    return beaker.session.Session({})


class Patches(object):
    @classmethod
    def sync_queue(self):
        def _synchronous_enqueue_job(job_func, args=None, kwargs=None, title=None, queue=None):
            '''
            Synchronous mock for ``ckan.plugins.toolkit.enqueue_job``.
            From https://docs.ckan.org/en/2.8/maintaining/background-tasks.html
            '''
            args = args or []
            kwargs = kwargs or {}
            job_func(*args, **kwargs)
            return mock.MagicMock()

        return mock.patch(u'ckan.plugins.toolkit.enqueue_job',
                          side_effect=_synchronous_enqueue_job)


class SimpleMock(object):
    '''A really basic mock class that just implements the attributes passed to it.'''
    def __init__(self, **k):
        for i in k:
            setattr(self, i, k[i])


class Response(mock.MagicMock):
    def raise_for_status(self):
        pass