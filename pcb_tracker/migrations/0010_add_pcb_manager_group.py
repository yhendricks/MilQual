from django.db import migrations
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType


def add_pcb_manager_group(apps, schema_editor):
    """Add the pcb_manager group with appropriate permissions"""
    
    # Get content types
    try:
        PCB = apps.get_model('pcb_tracker', 'PCB')
        Batch = apps.get_model('pcb_tracker', 'Batch')
        TestConfig = apps.get_model('pcb_tracker', 'TestConfig')
        PCBType = apps.get_model('pcb_tracker', 'PCBType')
        
        pcb_content_type = ContentType.objects.get_for_model(PCB)
        batch_content_type = ContentType.objects.get_for_model(Batch)
        test_config_content_type = ContentType.objects.get_for_model(TestConfig)
        pcb_type_content_type = ContentType.objects.get_for_model(PCBType)
    except LookupError:
        # Models don't exist yet, skip
        return
    
    # Get or create the pcb_manager group
    group, created = Group.objects.get_or_create(name='pcb_manager')
    
    # Define permissions for pcb_manager
    permissions = [
        # Full CRUD permissions for PCBs
        {'codename': 'add_pcb', 'content_type': pcb_content_type},
        {'codename': 'view_pcb', 'content_type': pcb_content_type},
        {'codename': 'change_pcb', 'content_type': pcb_content_type},
        {'codename': 'delete_pcb', 'content_type': pcb_content_type},
        
        # Can view related models
        {'codename': 'view_batch', 'content_type': batch_content_type},
        {'codename': 'view_testconfig', 'content_type': test_config_content_type},
        {'codename': 'view_pcbtype', 'content_type': pcb_type_content_type},
    ]
    
    # Assign permissions to the group
    for perm_data in permissions:
        try:
            perm = Permission.objects.get(
                codename=perm_data['codename'], 
                content_type=perm_data['content_type']
            )
            group.permissions.add(perm)
        except Permission.DoesNotExist:
            print(f"Permission {perm_data['codename']} does not exist")


def reverse_add_pcb_manager_group(apps, schema_editor):
    """Reverse the group creation"""
    try:
        group = Group.objects.get(name='pcb_manager')
        group.delete()
    except Group.DoesNotExist:
        pass


class Migration(migrations.Migration):

    dependencies = [
        ('pcb_tracker', '0009_add_test_config_permissions'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.RunPython(add_pcb_manager_group, reverse_add_pcb_manager_group),
    ]