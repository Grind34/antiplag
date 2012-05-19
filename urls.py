from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'antiplag.views.home', name='home'),
    # url(r'^antiplag/', include('antiplag.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', 'pagesmisc.views.main',name='main'),
    url(r'^exit/$', 'pagesmisc.views.exit',name='exit'),
    url(r'^login/$','pagesmisc.views.enter',name='login'),
)
