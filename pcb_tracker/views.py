from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Group, User
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.core.exceptions import PermissionDenied
from .models import PCB, Batch, TestMeasurement, FileAttachment, Module, ModuleTestRecord
from .forms import PCBTestForm, FileAttachmentForm, ModuleAssemblyForm, ModuleTestForm, PCBCreateForm


def user_in_group(user, group_names):
    """Check if user belongs to any of the specified groups"""
    return user.groups.filter(name__in=group_names).exists()


def can_test_pcb(user):
    """Check if user can test PCBs (board_tester groups)"""
    return user_in_group(user, ['board_tester_lvl1', 'board_tester_lvl2'])


def can_verify_pcb(user):
    """Check if user can verify PCBs (QA groups)"""
    return user_in_group(user, ['QA_lvl1', 'QA_lvl2'])


def can_assemble_module(user):
    """Check if user can assemble modules (assembler groups)"""
    return user_in_group(user, ['assembler_lvl1'])


def can_test_module(user):
    """Check if user can perform module tests (functional/environmental tester groups)"""
    return user_in_group(user, ['Function_tester_lvl1', 'Function_tester_lvl2', 
                                'Environmental_tester_lvl1'])


def can_verify_module(user):
    """Check if user can verify module tests (QA groups)"""
    return user_in_group(user, ['QA_lvl1', 'QA_lvl2'])


def is_manager(user):
    """Check if user is a manager"""
    return user_in_group(user, ['Manager_lvl1', 'Manager_lvl2'])


@login_required
def dashboard(request):
    """Main dashboard showing the status of PCBs and modules"""
    pcb_count = PCB.objects.count()
    pcb_pending = PCB.objects.filter(status='pending').count()
    pcb_tested = PCB.objects.filter(status='tested').count()
    pcb_qa_verified = PCB.objects.filter(status='qa_verified').count()
    
    module_count = Module.objects.count()
    modules_assembled = Module.objects.filter(status='assembled').count()
    modules_functional_tested = Module.objects.filter(status='functional_tested').count()
    
    context = {
        'pcb_count': pcb_count,
        'pcb_pending': pcb_pending,
        'pcb_tested': pcb_tested,
        'pcb_qa_verified': pcb_qa_verified,
        'module_count': module_count,
        'modules_assembled': modules_assembled,
        'modules_functional_tested': modules_functional_tested,
    }
    return render(request, 'pcb_tracker/dashboard.html', context)


@login_required
@user_passes_test(can_test_pcb)
def pcb_test(request):
    """View for board testers to enter PCB test measurements"""
    if request.method == 'POST':
        form = PCBTestForm(request.POST, user=request.user)
        attachment_form = FileAttachmentForm(request.POST, request.FILES)
        
        if form.is_valid() and attachment_form.is_valid():
            pcb = form.cleaned_data['pcb']
            
            # Create the test measurement
            measurement = TestMeasurement.objects.create(
                pcb=pcb,
                voltage=form.cleaned_data['voltage'],
                current=form.cleaned_data['current'],
                temperature=form.cleaned_data['temperature'],
                other_measurements=form.cleaned_data['other_measurements'],
                tester=request.user,
                notes=form.cleaned_data['notes']
            )
            
            # Handle file attachment if provided
            if 'file' in request.FILES:
                attachment = attachment_form.save(commit=False)
                attachment.pcb = pcb
                attachment.uploaded_by = request.user
                attachment.file_type = 'pcb_test'
                attachment.save()
            
            # Update PCB status
            pcb.status = 'tested'
            pcb.save()
            
            messages.success(request, f'PCB {pcb.serial_number} tested successfully!')
            return redirect('pcb_test')
    else:
        form = PCBTestForm(user=request.user)
        attachment_form = FileAttachmentForm()
    
    # Get PCBs that are pending testing
    pending_pcbs = PCB.objects.filter(status='pending')
    
    context = {
        'form': form,
        'attachment_form': attachment_form,
        'pending_pcbs': pending_pcbs,
    }
    return render(request, 'pcb_tracker/pcb_test.html', context)


@login_required
@user_passes_test(can_verify_pcb)
def pcb_qa_verify(request, pcb_id):
    """View for QA to verify PCB test results"""
    pcb = get_object_or_404(PCB, id=pcb_id)
    
    # Check if the PCB has been tested
    if pcb.status != 'tested':
        messages.error(request, 'This PCB has not been tested yet.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        # QA approves the PCB
        pcb.status = 'qa_verified'
        pcb.save()
        
        messages.success(request, f'PCB {pcb.serial_number} verified and approved by QA!')
        return redirect('dashboard')
    
    measurements = pcb.measurements.all()
    attachments = pcb.attachments.filter(file_type='pcb_test')
    
    context = {
        'pcb': pcb,
        'measurements': measurements,
        'attachments': attachments,
    }
    return render(request, 'pcb_tracker/pcb_qa_verify.html', context)


@login_required
@user_passes_test(can_assemble_module)
def module_assemble(request):
    """View for assemblers to create modules from approved PCBs"""
    if request.method == 'POST':
        form = ModuleAssemblyForm(request.POST)
        
        if form.is_valid():
            module = form.save(commit=False)
            module.assembler = request.user
            module.save()
            
            # Add PCBs to module and update their status
            pcbs = form.cleaned_data['pcbs']
            for pcb in pcbs:
                module.pcbs.add(pcb)
                
                # Update PCB status to assembled
                pcb.status = 'assembled'
                pcb.save()
            
            messages.success(request, f'Module {module.module_serial_number} assembled successfully!')
            return redirect('module_assemble')
    else:
        form = ModuleAssemblyForm()
    
    # Get PCBs that have been QA verified and not yet assembled
    available_pcbs = PCB.objects.filter(status='qa_verified')
    
    context = {
        'form': form,
        'available_pcbs': available_pcbs,
    }
    return render(request, 'pcb_tracker/module_assemble.html', context)


@login_required
@user_passes_test(can_test_module)
def module_functional_test(request):
    """View for functional testers to test modules"""
    if request.method == 'POST':
        form = ModuleTestForm(request.POST, request.FILES)
        
        if form.is_valid():
            module_test = form.save(commit=False)
            module_test.tester = request.user
            module_test.test_type = 'functional'
            module_test.save()
            
            # Update module status
            module = module_test.module
            module.status = 'functional_tested'
            module.save()
            
            messages.success(request, f'Module {module.module_serial_number} functional test recorded!')
            return redirect('module_functional_test')
    else:
        form = ModuleTestForm()
    
    # Get modules that are assembled and not yet functionally tested
    available_modules = Module.objects.filter(status='assembled')
    
    context = {
        'form': form,
        'available_modules': available_modules,
    }
    return render(request, 'pcb_tracker/module_functional_test.html', context)


@login_required
@user_passes_test(is_manager)
def module_sign_off(request):
    """View for managers to sign off completed modules"""
    # Get modules that have completed all required steps
    completed_modules = Module.objects.filter(status='completed')
    
    context = {
        'completed_modules': completed_modules,
    }
    return render(request, 'pcb_tracker/module_sign_off.html', context)


def pcb_detail(request, pcb_id):
    """View to show detailed information about a specific PCB"""
    pcb = get_object_or_404(PCB, id=pcb_id)
    measurements = pcb.measurements.all()
    attachments = pcb.attachments.all()
    modules = pcb.modules.all()
    
    context = {
        'pcb': pcb,
        'measurements': measurements,
        'attachments': attachments,
        'modules': modules,
    }
    return render(request, 'pcb_tracker/pcb_detail.html', context)


@login_required
@user_passes_test(is_manager)  # Only managers can create new PCBs
def pcb_create(request):
    """View for managers to create new PCB entries"""
    if request.method == 'POST':
        form = PCBCreateForm(request.POST)
        if form.is_valid():
            pcb = form.save()
            messages.success(request, f'PCB {pcb.serial_number} created successfully!')
            return redirect('pcb_create')
    else:
        form = PCBCreateForm()
    
    # Get all batches to show in the form
    batches = Batch.objects.all()
    
    context = {
        'form': form,
        'batches': batches,
    }
    return render(request, 'pcb_tracker/pcb_create.html', context)