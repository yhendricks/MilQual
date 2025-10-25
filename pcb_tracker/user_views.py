from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required


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
def delete_user(request, user_id):
    """Delete a user (only if current user is a superuser)"""
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission to delete users.')
        return redirect('dashboard')
    
    user_to_delete = User.objects.get(id=user_id)
    
    # Check if this is the last user
    if User.objects.count() == 1:
        messages.error(request, 'Cannot delete the last user.')
        return redirect('dashboard')
    
    # Check if this user to delete is the last user after deletion
    if User.objects.count() == 2 and user_to_delete.id == request.user.id:
        messages.error(request, 'Cannot delete yourself as you are the only other user.')
        return redirect('dashboard')
    
    username = user_to_delete.username
    user_to_delete.delete()
    
    # If the deleted user was the last one (other than the current user), make the current user a superuser
    if User.objects.count() == 1 and request.user.id != 1:  # Assuming ID 1 might be default superuser
        current_count = User.objects.count()
        if current_count == 1:
            # Find the remaining user (should be current user) and make them superuser
            remaining_user = User.objects.first()
            if remaining_user and not remaining_user.is_superuser:
                remaining_user.is_superuser = True
                remaining_user.is_staff = True
                remaining_user.save()
    
    messages.success(request, f'User {username} deleted successfully.')
    return redirect('dashboard')