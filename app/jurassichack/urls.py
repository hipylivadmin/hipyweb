from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

from . import views

app_name = 'jurassichack'

urlpatterns = [
    path('', views.index, name='index'),
    path('reset/', views.reset, name='reset'),
    path('console/', views.console, name='console'),
    path('<str:character_name>/', views.character, name='character'),
    path('input/<int:answer_id>/', views.input, name='input')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

