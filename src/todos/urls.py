from django.urls import path
from .views import BoardView, TaskCreateView, TaskDetailView

urlpatterns = [
    path("board", BoardView.as_view()),
    path("tasks", TaskCreateView.as_view()),
    path("tasks/<int:item_id>", TaskDetailView.as_view()),
]
