from django.urls import path
from .views import MessageListCreateView, MessageDownloadView, JsonFileView

urlpatterns = [
    path('topic/<int:topic_id>/messages/', MessageListCreateView.as_view(), name='message-list-create'),
    path('download/', MessageDownloadView.as_view(), name='download_file'),
    path('think/', JsonFileView.as_view(), name='think'),
]
