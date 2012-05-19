#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.db import models

class PublishedItems(models.Manager):
    def get_query_set(self):
        return super(self.__class__, self).get_query_set().filter(is_published=True)

class VisibleItems(models.Manager):
    def get_query_set(self):
        return super(self.__class__, self).get_query_set().filter(is_visible=True)

