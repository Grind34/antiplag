# -*- coding: utf-8 -*-

import re
import urlparse
import urllib

from BeautifulSoup import BeautifulSoup
from BeautifulSoup import Tag


def set_wmode_to_opaque(video_code):
    """
        Set wmode=opaque in object and embed tag
    """
    soup = BeautifulSoup(video_code)
    for object_tag in soup.findAll('object'):
        # find param tag with wmode and delete it
        for param_tag in object_tag.findChildren('param', attrs = {'name':'wmode'}):
            param_tag.extract()
        param_wmode_opaque = Tag(BeautifulSoup(), 'param', [('name','wmode'), ('value','opaque')])
        object_tag.insert(0, param_wmode_opaque)

    for embed_tag in soup.findAll('embed'):
        embed_tag['wmode'] = 'opaque'
    
    for iframe_tag in soup.findAll('iframe'):
        parsed = urlparse.urlparse(iframe_tag['src'])
        if parsed.hostname in ('youtube.com', 'www.youtube.com'):
            query = dict(urlparse.parse_qs(parsed[4], True))
            query.update({'wmode': ['opaque']})
            parsed = list(parsed)
            parsed[4] = urllib.urlencode(query, True)
            iframe_tag['src'] = urlparse.urlunparse(parsed)
    
    return unicode(soup)

def video_code_cleaning(video_code):
    """
        Clean tags from video_code.
        * Only object, param and embed elements are allow.
    """
    allowed_elements = [ 'object', 'param', 'embed', 'iframe']
    myMassage = [(re.compile('<!-*\[(.*?)\]>'), lambda match: '')]
    soup = BeautifulSoup(video_code, markupMassage=myMassage)
    for element in soup.findAll(True):
            if element.name not in allowed_elements:
                element.extract()
    return unicode(soup)
