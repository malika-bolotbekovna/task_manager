from django.urls import path
from .views import (
    ListListView, ListCreateView, ListUpdateView, ListDeleteView, ListDetailView,
    TaskListView, TaskCreateView, TaskUpdateView, TaskDeleteView,
    toggle_task_status, statistics_view,
)

urlpatterns = [
    path('', TaskListView.as_view(), name='task-list'),  # добавлено, корень сайта
    path('lists/', ListListView.as_view(), name='list-list'),
    path('lists/create/', ListCreateView.as_view(), name='list-create'),
    path('lists/<int:pk>/update/', ListUpdateView.as_view(), name='list-update'),
    path('lists/<int:pk>/delete/', ListDeleteView.as_view(), name='list-delete'),
    path('lists/<int:pk>/', ListDetailView.as_view(), name='list-detail'),

    path('tasks/', TaskListView.as_view(), name='task-list'),
    path('tasks/create/', TaskCreateView.as_view(), name='task-create'),
    path('tasks/<int:pk>/update/', TaskUpdateView.as_view(), name='task-update'),
    path('tasks/<int:pk>/delete/', TaskDeleteView.as_view(), name='task-delete'),

    path('tasks/<int:pk>/toggle/', toggle_task_status, name='task-toggle'),
    path('statistics/', statistics_view, name='statistics'),
]
