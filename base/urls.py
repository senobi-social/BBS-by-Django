from django.urls import path
from . import views
from django.views.generic import TemplateView

app_name = 'base'

urlpatterns = [
    path('', views.TopicListView.as_view(), name='top'),
    path('terms/', TemplateView.as_view(template_name='base/terms.html'), name='terms'), #TemplateViewを使って静的表示
    path('policy/', TemplateView.as_view(template_name='base/policy.html'), name='policy'),
    path('about/', TemplateView.as_view(template_name='base/about.html'), name='about'),
]

# path('', views.TopView.as_view(), name='top'),