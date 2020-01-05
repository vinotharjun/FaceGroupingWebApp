from django.conf.urls import url
from django.urls import path
from . import views
urlpatterns = [
    # url(r'^clear/$', views.clear_database, name='clear_database'),
    # path('backend', views.backend,name='backend'),
    path('',views.createfolder,name='createfolder'),
    path('getimages',views.getimages,name='getimages'),
    path('groupimages',views.groupimages,name='groupimages'),
    path('imageupload',views.imageupload,name='imageupload'),
    path('cluster',views.cluster,name='cluster')

]
