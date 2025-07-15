from django.urls import path
from .views import TopicListCreateView

urlpatterns = [
    path('', TopicListCreateView.as_view()),  # 基本的增删改查接口
]
