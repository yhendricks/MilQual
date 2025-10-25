from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Group, User
from django.contrib.auth import login
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import HttpResponseForbidden
from django.core.exceptions import PermissionDenied
from .models import PCB, Batch, TestMeasurement, FileAttachment, Module, ModuleTestRecord, PCBType, TestConfig, TestParameter, TestQuestion, ParameterMeasurement, QuestionResponse
from .forms import PCBTestForm, FileAttachmentForm, ModuleAssemblyForm, ModuleTestForm, PCBCreateForm, BatchCreateForm, PCBTypeForm


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


def can_view_production_summary(user):
    """Check if user can view production summary (specific group)"""
    return user_in_group(user, ['production_summary'])


@login_required
def dashboard(request):
    """Main dashboard showing the status of PCBs and modules"""
    # Check if user can view production summary
    can_view_summary = can_view_production_summary(request.user)
    
    # Only fetch counts if user can view summary
    if can_view_summary:
        pcb_count = PCB.objects.count()
        pcb_pending = PCB.objects.filter(status='pending').count()
        pcb_tested = PCB.objects.filter(status='tested').count()
        pcb_qa_verified = PCB.objects.filter(status='qa_verified').count()
        
        module_count = Module.objects.count()
        modules_assembled = Module.objects.filter(status='assembled').count()
        modules_functional_tested = Module.objects.filter(status='functional_tested').count()
    else:
        # Set default values if user can't view summary
        pcb_count = pcb_pending = pcb_tested = pcb_qa_verified = 0
        module_count = modules_assembled = modules_functional_tested = 0
    
    # Get batches for managers
    batches = Batch.objects.all() if is_manager(request.user) else Batch.objects.none()
    
    context = {
        'pcb_count': pcb_count,
        'pcb_pending': pcb_pending,
        'pcb_tested': pcb_tested,
        'pcb_qa_verified': pcb_qa_verified,
        'module_count': module_count,
        'modules_assembled': modules_assembled,
        'modules_functional_tested': modules_functional_tested,
        'batches': batches,
        'can_view_summary': can_view_summary,
    }
    return render(request, 'pcb_tracker/dashboard.html', context)


@login_required
@user_passes_test(is_manager)  # Only managers can create PCB types
def pcb_type_manage(request):
    """View for managing PCB types with CRUD operations"""
    if request.method == 'POST':
        if 'create' in request.POST:
            form = PCBTypeForm(request.POST)
            if form.is_valid():
                pcb_type = form.save()
                messages.success(request, f'PCB Type {pcb_type.name} created successfully!')
                return redirect('pcb_type_manage')
        elif 'update' in request.POST:
            pcb_type_id = request.POST.get('pcb_type_id')
            pcb_type = get_object_or_404(PCBType, id=pcb_type_id)
            form = PCBTypeForm(request.POST, instance=pcb_type)
            if form.is_valid():
                form.save()
                messages.success(request, f'PCB Type {pcb_type.name} updated successfully!')
                return redirect('pcb_type_manage')
        elif 'delete' in request.POST:
            pcb_type_id = request.POST.get('pcb_type_id')
            pcb_type = get_object_or_404(PCBType, id=pcb_type_id)
            pcb_type_name = pcb_type.name
            pcb_type.delete()
            messages.success(request, f'PCB Type {pcb_type_name} deleted successfully!')
            return redirect('pcb_type_manage')
    else:
        form = PCBTypeForm()
    
    # Get all existing PCB types and paginate them
    pcb_types = PCBType.objects.all().order_by('name')
    paginator = Paginator(pcb_types, 10)  # Show 10 PCB types per page
    page_number = request.GET.get('page')
    pcb_types_page = paginator.get_page(page_number)
    
    context = {
        'form': form,
        'pcb_types': pcb_types_page,
    }
    return render(request, 'pcb_tracker/pcb_type_manage.html', context)


@login_required
@user_passes_test(is_manager)  # Only managers can manage batches
def batch_manage(request):
    """View for managing batches with CRUD operations"""
    if request.method == 'POST':
        if 'create' in request.POST:
            form = BatchCreateForm(request.POST)
            if form.is_valid():
                batch = form.save()
                messages.success(request, f'Batch {batch.batch_number} created successfully!')
                return redirect('batch_manage')
        elif 'update' in request.POST:
            batch_id = request.POST.get('batch_id')
            batch = get_object_or_404(Batch, id=batch_id)
            form = BatchCreateForm(request.POST, instance=batch)
            if form.is_valid():
                form.save()
                messages.success(request, f'Batch {batch.batch_number} updated successfully!')
                return redirect('batch_manage')
        elif 'delete' in request.POST:
            batch_id = request.POST.get('batch_id')
            batch = get_object_or_404(Batch, id=batch_id)
            batch_number = batch.batch_number
            
            # Check if the batch has any PCBs associated with it
            if batch.pcbs.count() > 0:
                messages.error(request, f'Cannot delete batch {batch_number} because it contains {batch.pcbs.count()} PCB(s). Remove PCBs first.')
                return redirect('batch_manage')
            
            batch.delete()
            messages.success(request, f'Batch {batch_number} deleted successfully!')
            return redirect('batch_manage')
    else:
        form = BatchCreateForm()
    
    # Force refresh the form's queryset for the PCBType field
    form.fields['pcb_type'].queryset = PCBType.objects.all()
    
    # Get all existing batches and paginate them
    batches = Batch.objects.all().order_by('-production_date')
    paginator = Paginator(batches, 10)  # Show 10 batches per page
    page_number = request.GET.get('page')
    batches_page = paginator.get_page(page_number)
    
    # Pass PCB types directly to template context for modal
    pcb_types_for_modal = PCBType.objects.all()
    
    context = {
        'form': form,
        'batches': batches_page,
        'pcb_types_for_modal': pcb_types_for_modal,
    }
    return render(request, 'pcb_tracker/batch_manage.html', context)


@login_required
def pcb_test(request):
    """View for board testers to enter PCB test measurements based on test configuration"""
    if request.method == 'POST':
        # First, check if we're submitting test data for a specific PCB
        pcb_serial = request.POST.get('pcb_serial')
        
        if pcb_serial:
            try:
                pcb = PCB.objects.get(serial_number=pcb_serial, status='pending')
                
                # Create the main test measurement record
                test_measurement = TestMeasurement.objects.create(
                    pcb=pcb,
                    test_config=pcb.test_config,
                    tester=request.user,
                    notes=request.POST.get('notes', '')
                )
                
                # Process parameter measurements if PCB has a test config
                if pcb.test_config:
                    for parameter in pcb.test_config.parameters.all():
                        param_value = request.POST.get(f'param_{parameter.id}')
                        if param_value:
                            try:
                                value = float(param_value)
                                ParameterMeasurement.objects.create(
                                    test_measurement=test_measurement,
                                    test_parameter=parameter,
                                    value=value,
                                    unit=parameter.unit
                                )
                            except ValueError:
                                # Handle invalid numeric input
                                messages.error(request, f'Invalid value for {parameter.name}')
                                # Clean up partial data and continue
                                test_measurement.delete()
                                break
                
                # Process question responses if PCB has a test config
                if pcb.test_config:
                    for question in pcb.test_config.questions.all():
                        response_value = request.POST.get(f'question_{question.id}')
                        if response_value:
                            try:
                                response_bool = response_value.lower() == 'true'
                                QuestionResponse.objects.create(
                                    test_measurement=test_measurement,
                                    test_question=question,
                                    response=response_bool
                                )
                            except:
                                # Handle invalid boolean input
                                messages.error(request, f'Invalid response for question: {question.question_text}')
                                # Clean up partial data and continue
                                test_measurement.delete()
                                break
                
                # Handle file attachment if provided
                if request.FILES.get('file'):
                    attachment = FileAttachment(
                        pcb=pcb,
                        file_type='pcb_test',
                        file=request.FILES['file'],
                        uploaded_by=request.user,
                        description=request.POST.get('file_description', '')
                    )
                    attachment.save()
                
                # Update PCB status
                pcb.status = 'tested'
                pcb.save()
                
                messages.success(request, f'PCB {pcb.serial_number} tested successfully!')
                return redirect('pcb_test')
                
            except PCB.DoesNotExist:
                messages.error(request, 'PCB with this serial number does not exist or is not available for testing.')
    
    # Get PCBs that are pending testing with search and pagination
    search_query = request.GET.get('search', '')
    
    pending_pcbs = PCB.objects.filter(status='pending')
    
    if search_query:
        pending_pcbs = pending_pcbs.filter(serial_number__icontains=search_query)
    
    # Add pagination
    paginator = Paginator(pending_pcbs, 10)  # 10 PCBs per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'pending_pcbs': page_obj,  # Paginated and filtered results
        'search_query': search_query,
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


def register(request):
    """Register a new user"""
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        
        # Basic validation
        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'registration/register.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return render(request, 'registration/register.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return render(request, 'registration/register.html')
        
        # Create user
        user = User.objects.create_user(username=username, email=email, password=password1)
        
        # Check if this is the first user (no other users exist)
        if User.objects.count() == 1:  # Just this new user
            user.is_superuser = True
            user.is_staff = True
            user.save()
            messages.success(request, 'Registration successful! You are now a superuser.')
        else:
            messages.success(request, 'Registration successful!')
        
        login(request, user)
        return redirect('dashboard')
    
    return render(request, 'registration/register.html')


@login_required
def profile(request):
    """User profile page"""
    if request.method == 'POST':
        # Update user profile information
        user = request.user
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        
        # Check if username is taken by another user
        if username and username != user.username:
            if User.objects.filter(username=username).exclude(id=user.id).exists():
                messages.error(request, 'Username already exists.')
                return render(request, 'pcb_tracker/profile.html', {'user': user})
        
        # Check if email is taken by another user
        if email and email != user.email:
            if User.objects.filter(email=email).exclude(id=user.id).exists():
                messages.error(request, 'Email already exists.')
                return render(request, 'pcb_tracker/profile.html', {'user': user})
        
        # Update user fields
        if username: user.username = username
        if email: user.email = email
        if first_name: user.first_name = first_name
        if last_name: user.last_name = last_name
        
        user.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')
    
    return render(request, 'pcb_tracker/profile.html', {'user': request.user})