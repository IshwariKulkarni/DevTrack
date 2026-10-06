from django.urls import path

from issues.views import issues, reporters

urlpatterns = [
    path('reporters/', reporters, name='reporters'),
    path('issues/', issues, name='issues'),
]