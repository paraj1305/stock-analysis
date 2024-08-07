from django.contrib import admin
from django.urls import path, include
from analysis import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('analysis/', include('analysis.urls')),
    
]
