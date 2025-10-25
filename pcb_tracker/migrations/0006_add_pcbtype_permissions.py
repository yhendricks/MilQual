from django.db import migrations
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from pcb_tracker.models import PCBType


def update_group_permissions(apps, schema_editor):
    """Update group permissions to include PCBType permissions"""
    
    pcb_type_content_type = ContentType.objects.get_for_model(apps.get_model('pcb_tracker', 'PCBType'))
    
    # Define the new permissions
    pcb_type_permissions = {
        'Manager_lvl1': [
            {'codename': 'add_pcbtype', 'content_type': pcb_type_content_type},
            {'codename': 'view_pcbtype', 'content_type': pcb_type_content_type},
            {'codename': 'change_pcbtype', 'content_type': pcb_type_content_type},
            {'codename': 'delete_pcbtype', 'content_type': pcb_type_content_type},
        ],
        'Manager_lvl2': [
            {'codename': 'add_pcbtype', 'content_type': pcb_type_content_type},
            {'codename': 'view_pcbtype', 'content_type': pcb_type_content_type},
            {'codename': 'change_pcbtype', 'content_type': pcb_type_content_type},
            {'codename': 'delete_pcbtype', 'content_type': pcb_type_content_type},
        ],
        'Admin': [
            {'codename': 'add_pcbtype', 'content_type': pcb_type_content_type},
            {'codename': 'view_pcbtype', 'content_type': pcb_type_content_type},
            {'codename': 'change_pcbtype', 'content_type': pcb_type_content_type},
            {'codename': 'delete_pcbtype', 'content_type': pcb_type_content_type},
        ],
    }
    
    # Assign permissions to each group
    for group_name, perms in pcb_type_permissions.items():
        try:
            group = Group.objects.get(name=group_name)
            for perm_data in perms:
                try:
                    perm = Permission.objects.get(codename=perm_data['codename'], content_type=perm_data['content_type'])
                    group.permissions.add(perm)
                except Permission.DoesNotExist:
                    print(f"Permission {perm_data['codename']} does not exist for content type {perm_data['content_type']}")
        except Group.DoesNotExist:
            print(f"Group {group_name} does not exist")


def reverse_update_group_permissions(apps, schema_editor):
    """Reverse the permission updates"""
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')
    ContentType = apps.get_model('contenttypes', 'ContentType')
    
    pcb_type_content_type = ContentType.objects.get_for_model(apps.get_model('pcb_tracker', 'PCBType'))
    
    # Get all PCBType related permissions
    pcb_type_perms = Permission.objects.filter(content_type=pcb_type_content_type)
    
    # Remove these permissions from the groups
    for group_name in ['Manager_lvl1', 'Manager_lvl2', 'Admin']:
        try:
            group = Group.objects.get(name=group_name)
            for perm in pcb_type_perms:
                group.permissions.remove(perm)
        except Group.DoesNotExist:
            pass  # Group doesn't exist, continue


class Migration(migrations.Migration):

    dependencies = [
        ('pcb_tracker', '0005_pcbtype_batch_pcb_type'),
    ]

    operations = [
        migrations.RunPython(update_group_permissions, reverse_update_group_permissions),
    ]