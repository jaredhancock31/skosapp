from django.conf.urls import url, include
from django.contrib import admin
from skosapp import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^', include('skosapp.urls')),

]
