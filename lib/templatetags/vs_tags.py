# -*- mode: python; coding: utf-8; -*-

from django import template
import re 

register = template.Library()

@register.filter
def strict_spaces(value, params):
    params = params.split(r':')
    
    try: max_length = int(params[0])
    except (ValuerError, IndexError): max_length = 0
     
    try: more_text = params[1]
    except IndexError: more_text = '...'

    value = re.sub(r'\s+',' ', re.sub(r'(?i)&nbsp;',' ',value)).strip()
    return value if max_length < 1 or len(value) <= max_length else value[:max_length-len(more_text)]+more_text
