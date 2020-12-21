from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from . import views

app_name = 'memes'
urlpatterns = [
                  path('', views.IndexView.as_view(), name='index'),
                  path('upload', views.upload, name='upload'),
                  path('<int:pk>/image', views.ImageSrcView.as_view(), name='image'),
                  path('<int:pk>/meme', views.MemView.as_view(), name='meme'),
                  path('<int:image_id>/set_text/', views.set_text, name='set_text'),
                  path('<int:mem_id>/download/', views.download, name='download'),
              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


