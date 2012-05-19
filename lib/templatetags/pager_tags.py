#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django import template
from django.template import Node

import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('pager-templatetag')

register = template.Library()

class Pages:
    def __init__(self, page, segment):
        self.page = page.number
        self.pages = page.paginator.num_pages
        self.left = []
        self.middle = []
        self.right = []
        self.next = None
        self.previous = None

        if self.page > 1:
            self.previous = self.page - 1

        p = int(1)

        while p < segment and p <= self.pages:
            self.left.append(p)
            p = p + 1

        if p < self.page - segment/2:
            p = self.page - segment/2 + 1
        if p > segment:
            while p < self.page + segment/2 and p <= self.pages:
                self.middle.append(int(p))
                p = p + 1
        else:
            while p < self.page + segment/2 and p <= self.pages:
                self.left.append(int(p))
                p = p + 1

        if p < self.pages - segment/2:
            p = self.pages - segment/2
        if p > self.pages - segment/2:
            while p < self.pages:
                self.middle.append(int(p))
                p = p + 1
        else:
            while p <= self.pages:
                self.right.append(int(p))
                p = p + 1

        if self.page < self.pages:
            self.next = self.page + 1

class PaginationNode(Node):
    def __init__(self, page_var, segment):
        self.page_var = page_var
        self.segment = int(segment)

    def render(self, context):
        page = template.resolve_variable(self.page_var, context)
        try:
            context['pagination'] = Pages(page, self.segment)
        except:
            pass

        return ''

def paginate(_parser, token):
    tokens = token.contents.split()
    if len(tokens) != 3:
        raise template.TemplateSyntaxError, "pagination tag takes page and segment as arguments"
    return PaginationNode(tokens[1], tokens[2])

register.tag('paginate', paginate)
