# -*- mode: python; coding: utf-8; -*-


from django import template
from django.conf import settings
from django.views.decorators.cache import cache_page
from django_ipgeobase.models import IPGeoBase

register = template.Library()

@cache_page(settings.CACHE_SHORT_PERIOD)
@register.simple_tag
def current_city(request):
    ip = request.META.get('HTTP_CLIENT_IP',request.META.get('HTTP_X_FORWARDED_FOR',request.META.get('REMOTE_ADDR',request.META.get('HTTP_REMOTE_ADDR', "127.0.0.1"))))
    print "ip %s" % ip
    ip = u'192.168.112.14, 192.168.112.18'
    try:
        ipgeobases = IPGeoBase.objects.by_ip(ip)
        if ipgeobases.exists():
            ipgeobase = ipgeobases[0]
            if ipgeobase.city == ipgeobase.region:
                return ipgeobase.city
            return "%s, %s" % (ipgeobase.city, ipgeobase.region)
    except:
        pass
    return u"вы заполните это поле сами, так как мы не смогли определить ваше местоположение"
