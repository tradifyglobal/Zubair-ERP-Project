from django.urls import path
from . import views

app_name = 'projects'

urlpatterns = [
    path('dashboard/', views.ProjectDashboardView.as_view(), name='dashboard'),
    path('', views.ProjectListView.as_view(), name='project_list'),
    path('create/', views.ProjectCreateView.as_view(), name='project_create'),
    path('<int:pk>/', views.ProjectDetailView.as_view(), name='project_detail'),
    path('<int:pk>/edit/', views.ProjectUpdateView.as_view(), name='project_edit'),
    path('tasks/', views.TaskListView.as_view(), name='task_list'),
    path('tasks/create/', views.TaskCreateView.as_view(), name='task_create'),
    path('tasks/<int:pk>/edit/', views.TaskUpdateView.as_view(), name='task_edit'),
    path('time-entries/', views.TimeEntryListView.as_view(), name='timeentry_list'),
    path('time-entries/create/', views.TimeEntryCreateView.as_view(), name='timeentry_create'),
    path('time-entries/<int:pk>/edit/', views.TimeEntryUpdateView.as_view(), name='timeentry_edit'),
]
