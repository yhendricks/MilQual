from django.db import migrations
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from pcb_tracker.models import UserGroupExtension


def create_manage_pcb_type_group(apps, schema_editor):
    """Create a group specifically for managing PCB types"""
    Group = apps.get_model('auth', 'Group')
    UserGroupExtension = apps.get_model('pcb_tracker', 'UserGroupExtension')
    Permission = apps.get_model('auth', 'Permission')
    ContentType = apps.get_model('contenttypes', 'ContentType')
    
    # Get PCBType content type
    pcb_type_content_type = ContentType.objects.get_for_model(apps.get_model('pcb_tracker', 'PCBType'))
    
    # Create the manage_pcb_type group
    group, created = Group.objects.get_or_create(name='manage_pcb_type')
    
    if created:
        # Create extension for the group
        extension = UserGroupExtension.objects.create(
            group=group,
            level=0,  # Default level
            department='Production',
            description='Group that can manage PCB types (CRUD)'
        )
        
        # Add PCBType permissions to the group
        pcb_type_permissions = [
            {'codename': 'add_pcbtype', 'content_type': pcb_type_content_type},
            {'codename': 'view_pcbtype', 'content_type': pcb_type_content_type},
            {'codename': 'change_pcbtype', 'content_type': pcb_type_content_type},
            {'codename': 'delete_pcbtype', 'content_type': pcb_type_content_type},
        ]
        
        for perm_data in pcb_type_permissions:
            try:
                perm = Permission.objects.get(codename=perm_data['codename'], content_type=perm_data['content_type'])
                group.permissions.add(perm)
            except Permission.DoesNotExist:
                print(f"Permission {perm_data['codename']} does not exist for content type {perm_data['content_type']}")


def reverse_create_manage_pcb_type_group(apps, schema_editor):
    """Reverse the group creation"""
    Group = apps.get_model('auth', 'Group')
    UserGroupExtension = apps.get_model('pcb_tracker', 'UserGroupExtension')
    
    try:
        extension = UserGroupExtension.objects.get(group__name='manage_pcb_type')
        extension.delete()
        Group.objects.get(name='manage_pcb_type').delete()
    except:
        pass  # Group doesn't exist, continue


class Migration(migrations.Migration):

    dependencies = [
        ('pcb_tracker', '0006_add_pcbtype_permissions'),
    ]

    operations = [
        migrations.RunPython(create_manage_pcb_type_group, reverse_create_manage_pcb_type_group),
    ]