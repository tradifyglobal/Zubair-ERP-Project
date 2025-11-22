from django.urls import path
from . import views

app_name = 'projects'

urlpatterns = [
    path('dashboard/', views.ProjectDashboardView.as_view(), name='dashboard'),
    path('', views.ProjectListView.as_view(), name='project_list'),
    path('<int:pk>/', views.ProjectDetailView.as_view(), name='project_detail'),
    path('tasks/', views.TaskListView.as_view(), name='task_list'),
    path('time-entries/', views.TimeEntryListView.as_view(), name='timeentry_list'),
]
