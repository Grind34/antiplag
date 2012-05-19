#!/usr/bin/env python
# -*- coding: utf-8 -*-
from BeautifulSoup import BeautifulSoup, Comment
from django import template
register = template.Library()

def sanitize_html(value):
    import re
    valid_tags = 'a strong em code br ul li img ol'.split()
    valid_attrs = 'href src title'.split()
    soup = BeautifulSoup(value)
    for comment in soup.findAll(
        text=lambda text: isinstance(text, Comment)):
        comment.extract()
    for tag in soup.findAll(True):
        if tag.name not in valid_tags:
            tag.hidden = True
        else:
            for attr, val in tag.attrs:
                if re.match('javascript:', val, re.I) is not None:
                    tag.hidden = True
            tag.attrs = [(attr, val) for attr, val in tag.attrs if attr in valid_attrs]

    return soup.renderContents().decode('utf8')
register.filter('sanitize', sanitize_html)
