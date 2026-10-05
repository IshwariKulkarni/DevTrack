from django.urls import path

from issues.views import reporters

urlpatterns = [
    path('reporters/', reporters, name='reporters'),
]