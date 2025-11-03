from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from .models import CompanyProfile, AttendanceRule, WorkWeek
from .forms import CompanyProfileForm, AttendanceRuleForm, WorkWeekForm

@login_required
def settings_view(request):
    """Settings management page"""
    company_profile = CompanyProfile.objects.first()
    attendance_rules = AttendanceRule.objects.all()
    work_week = WorkWeek.objects.all().order_by('day')

    context = {
        'user_role': 'Admin',
        'company_profile': company_profile,
        'attendance_rules': attendance_rules,
        'work_week': work_week,
    }
    return render(request, 'settings/settings.html', context)

# Company Profile CRUD
@login_required
def edit_company_profile(request):
    company_profile = CompanyProfile.objects.first()
    if not company_profile:
        company_profile = CompanyProfile()

    if request.method == 'POST':
        form = CompanyProfileForm(request.POST, instance=company_profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Company profile updated successfully.')
            return redirect('settings')
    else:
        form = CompanyProfileForm(instance=company_profile)

    return render(request, 'settings/edit_company_profile.html', {
        'form': form,
        'user_role': 'Admin'
    })

# Attendance Rules CRUD
@login_required
def add_attendance_rule(request):
    if request.method == 'POST':
        form = AttendanceRuleForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Attendance rule added successfully.')
            return redirect('settings')
    else:
        form = AttendanceRuleForm()
    return render(request, 'settings/add_attendance_rule.html', {'form': form, 'user_role': 'Admin'})

@login_required
def edit_attendance_rule(request, rule_id):
    rule = get_object_or_404(AttendanceRule, id=rule_id)
    if request.method == 'POST':
        form = AttendanceRuleForm(request.POST, instance=rule)
        if form.is_valid():
            form.save()
            messages.success(request, 'Attendance rule updated successfully.')
            return redirect('settings')
    else:
        form = AttendanceRuleForm(instance=rule)
    return render(request, 'settings/edit_attendance_rule.html', {'form': form, 'rule': rule, 'user_role': 'Admin'})

@login_required
@require_POST
def delete_attendance_rule(request, rule_id):
    rule = get_object_or_404(AttendanceRule, id=rule_id)
    rule.delete()
    messages.success(request, 'Attendance rule deleted successfully.')
    return redirect('settings')

# Work Week CRUD
@login_required
def edit_work_week(request):
    work_week_days = WorkWeek.objects.all().order_by('id')

    if request.method == 'POST':
        # Handle bulk update for work week
        for day in work_week_days:
            is_working = request.POST.get(f'is_working_{day.id}') == 'on'
            day.is_working_day = is_working
            day.save()

        messages.success(request, 'Work week settings updated successfully.')
        return redirect('settings')

    return render(request, 'settings/edit_work_week.html', {
        'work_week': work_week_days,
        'user_role': 'Admin'
    })

@login_required
def update_work_week_day(request, day_id):
    """AJAX endpoint to update individual work week day"""
    if request.method == 'POST':
        day = get_object_or_404(WorkWeek, id=day_id)
        day.is_working_day = request.POST.get('is_working') == 'true'
        day.save()
        return JsonResponse({'success': True})

    return JsonResponse({'success': False})
