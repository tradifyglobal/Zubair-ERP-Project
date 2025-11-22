from django.contrib import admin
from .models import (
    Project, ProjectPhase, Task, ResourceAllocation,
    ProjectBudget, TimeEntry, ProjectKPI, ProjectSettings
)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('project_code', 'project_name', 'status', 'priority', 'project_manager', 'budgeted_amount', 'completion_percentage')
    list_filter = ('entity', 'status', 'priority', 'start_date')
    search_fields = ('project_code', 'project_name')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'start_date'


@admin.register(ProjectPhase)
class ProjectPhaseAdmin(admin.ModelAdmin):
    list_display = ('project', 'phase_name', 'sequence', 'status', 'start_date', 'end_date', 'completion_percentage')
    list_filter = ('status', 'project__status')
    search_fields = ('phase_name', 'project__project_code')


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('project', 'task_name', 'status', 'assigned_to', 'due_date', 'estimated_hours', 'actual_hours')
    list_filter = ('status', 'project', 'assigned_to', 'due_date')
    search_fields = ('task_name', 'project__project_code')
    date_hierarchy = 'due_date'


@admin.register(ResourceAllocation)
class ResourceAllocationAdmin(admin.ModelAdmin):
    list_display = ('project', 'employee', 'allocation_start_date', 'allocation_end_date', 'hours_per_week', 'hourly_rate')
    list_filter = ('is_active', 'project', 'employee')
    search_fields = ('employee__first_name', 'employee__last_name', 'project__project_code')


@admin.register(ProjectBudget)
class ProjectBudgetAdmin(admin.ModelAdmin):
    list_display = ('project', 'category', 'budgeted_amount', 'actual_amount', 'committed_amount')
    list_filter = ('category', 'project')


@admin.register(TimeEntry)
class TimeEntryAdmin(admin.ModelAdmin):
    list_display = ('project', 'employee', 'entry_date', 'hours_worked', 'cost', 'is_billable')
    list_filter = ('entry_date', 'project', 'is_billable', 'employee')
    search_fields = ('project__project_code', 'employee__first_name')
    date_hierarchy = 'entry_date'


@admin.register(ProjectKPI)
class ProjectKPIAdmin(admin.ModelAdmin):
    list_display = ('project', 'kpi_name', 'target_value', 'actual_value', 'status', 'measurement_date')
    list_filter = ('status', 'measurement_date', 'project')


@admin.register(ProjectSettings)
class ProjectSettingsAdmin(admin.ModelAdmin):
    list_display = ('entity', 'require_budget_approval', 'require_time_entry', 'project_code_prefix')
    readonly_fields = ('created_at', 'updated_at')
