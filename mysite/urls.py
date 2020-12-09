"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.urls import path, include
from django.conf import settings # debug tool
import base

# サイトマップ
from django.contrib.sitemaps.views import sitemap
from thread.sitemaps import TopicSitemap, CategorySitemap
from base.sitemaps import BaseSitemap

# ファイルの取り扱い
from django.conf.urls.static import static
  
sitemaps = {
    'topic': TopicSitemap,
    'cateogry': CategorySitemap,
    'base': BaseSitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('base.urls')),
    path('thread/', include('thread.urls')),
    path('api/', include('api.urls')),
    path('search/', include('search.urls')),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}), # サイトマップ
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) # ファイルの取り扱い

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns