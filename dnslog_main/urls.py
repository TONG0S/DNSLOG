from django.urls import path
from dnslog_main import views
urlpatterns = [
    # path('about_me/',views.about_me,name='about_me'),
    path('main/',views.main,name='main'),
    path('about/',views.main,name='main'),
]