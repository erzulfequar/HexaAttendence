from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Department, Designation, Shift, Employee, Device, Holiday, Task, TaskSubmission
from .forms import TaskForm  # We'll create this form

@login_required
def master_view(request):
    """Master data management page"""
    departments = Department.objects.all()
    designations = Designation.objects.all()
    shifts = Shift.objects.all()
    employees = Employee.objects.select_related('department', 'designation', 'shift').all()
    devices = Device.objects.all()
    holidays = Holiday.objects.all()
    tasks = Task.objects.select_related('allotted_employee', 'approved_by').all()

    context = {
        'user_role': 'Admin',
        'departments': departments,
        'designations': designations,
        'shifts': shifts,
        'employees': employees,
        'devices': devices,
        'holidays': holidays,
        'tasks': tasks,
    }
    return render(request, 'master/master.html', context)

@login_required
def create_task(request):
    """Create a new task for an employee"""
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            # For now, set approved_by to None or a default user if needed
            task.approved_by = None  # Or set to a default user if available
            task.save()
            messages.success(request, 'Task created successfully!')

            # Check if this is an AJAX request
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': 'Task created successfully!'})
            else:
                return redirect('master')
        else:
            # Handle form errors for AJAX
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = TaskForm()

    # Return JSON error for AJAX requests
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'message': 'Invalid request method'})

    return render(request, 'master/create_task.html', {'form': form})

@login_required
def task_detail(request, task_id):
    """View task details and submissions"""
    task = get_object_or_404(Task, pk=task_id)
    submissions = TaskSubmission.objects.filter(task=task).select_related('submitted_by')
    return render(request, 'master/task_detail.html', {
        'task': task,
        'submissions': submissions
    })

@login_required
def update_task_status(request, task_id):
    """Update task status"""
    task = get_object_or_404(Task, pk=task_id)
    if request.method == 'POST':
        status = request.POST.get('status')
        if status in ['pending', 'in_progress', 'completed', 'cancelled']:
            task.status = status
            task.save()
            messages.success(request, f'Task status updated to {status}!')
        return redirect('task_detail', task_id=task_id)
    return redirect('master_view')
