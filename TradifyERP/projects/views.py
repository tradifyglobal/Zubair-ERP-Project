from django.shortcuts import render
from django.views.generic import ListView, DetailView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, Q, F
from django.utils import timezone
from datetime import timedelta

from .models import Project, Task, TimeEntry, ResourceAllocation, ProjectKPI


class ProjectDashboardView(LoginRequiredMixin, TemplateView):
    """Project Management Dashboard."""
    template_name = 'projects/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Active projects
        active_projects = Project.objects.filter(
            status__in=['ACTIVE', 'PLANNING']
        ).order_by('-start_date')[:10]
        
        # Budget overview
        total_budgeted = Project.objects.aggregate(
            total=Sum('budgeted_amount')
        )['total'] or 0
        total_actual = Project.objects.aggregate(
            total=Sum('actual_cost')
        )['total'] or 0
        
        # Overdue tasks
        overdue_tasks = Task.objects.filter(
            status__in=['TODO', 'IN_PROGRESS'],
            due_date__lt=timezone.now().date()
        )
        
        # Time entries (last 7 days)
        recent_entries = TimeEntry.objects.filter(
            entry_date__gte=timezone.now().date() - timedelta(days=7)
        ).select_related('employee', 'project')
        
        context.update({
            'active_projects': active_projects,
            'total_budgeted': total_budgeted,
            'total_actual': total_actual,
            'overdue_tasks': overdue_tasks.count(),
            'recent_entries': recent_entries,
            'total_active_projects': Project.objects.filter(status='ACTIVE').count(),
        })
        
        return context


class ProjectListView(LoginRequiredMixin, ListView):
    """List all projects."""
    model = Project
    template_name = 'projects/project_list.html'
    context_object_name = 'projects'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Project.objects.select_related('project_manager', 'department').order_by('-start_date')
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        return queryset


class ProjectDetailView(LoginRequiredMixin, DetailView):
    """Detail view for project."""
    model = Project
    template_name = 'projects/project_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['phases'] = self.object.phases.all().order_by('sequence')
        context['tasks'] = self.object.tasks.all()
        context['resources'] = self.object.resource_allocations.filter(is_active=True)
        context['budget_lines'] = self.object.budget_lines.all()
        context['time_entries'] = self.object.time_entries.order_by('-entry_date')[:20]
        context['kpis'] = self.object.kpis.all()
        return context


class TaskListView(LoginRequiredMixin, ListView):
    """List all tasks."""
    model = Task
    template_name = 'projects/task_list.html'
    context_object_name = 'tasks'
    paginate_by = 50
    
    def get_queryset(self):
        queryset = Task.objects.select_related('project', 'assigned_to').order_by('-due_date')
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        return queryset


class TimeEntryListView(LoginRequiredMixin, ListView):
    """List time entries."""
    model = TimeEntry
    template_name = 'projects/timeentry_list.html'
    context_object_name = 'entries'
    paginate_by = 50
    
    def get_queryset(self):
        return TimeEntry.objects.select_related('project', 'employee', 'task').order_by('-entry_date')
