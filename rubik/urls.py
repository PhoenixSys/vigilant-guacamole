"""
URL configuration for rubik project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import path, include
from django.views.generic.base import RedirectView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('accounts/', include('django.contrib.auth.urls')), # For login, logout, password change
    path('favicon.ico', RedirectView.as_view(url='/static/favicon.ico', permanent=True)),
    # Other app urls can go here
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# It's good practice to also add a root path if not already present,
# for example, redirecting to the main app's home or a dedicated landing page.
# from django.views.generic import RedirectView
# urlpatterns += [path('', RedirectView.as_view(url='/accounts/', permanent=True)),]
# Or, if you have a site-wide landing page that's not in 'accounts':
# from my_main_app import views as main_views
# urlpatterns += [path('', main_views.landing_page, name='landing_page'),]
