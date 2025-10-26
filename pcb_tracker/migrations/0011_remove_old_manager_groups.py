from django.db import migrations
from django.contrib.auth.models import Group


def remove_old_manager_groups(apps, schema_editor):
    """Remove the old Manager_lvl1 and Manager_lvl2 groups"""
    Group = apps.get_model('auth', 'Group')
    
    # Remove the old manager groups
    try:
        Group.objects.get(name='Manager_lvl1').delete()
    except Group.DoesNotExist:
        pass  # Group doesn't exist, continue
    
    try:
        Group.objects.get(name='Manager_lvl2').delete()
    except Group.DoesNotExist:
        pass  # Group doesn't exist, continue


def reverse_remove_old_manager_groups(apps, schema_editor):
    """Recreate the old Manager_lvl1 and Manager_lvl2 groups"""
    Group = apps.get_model('auth', 'Group')
    UserGroupExtension = apps.get_model('pcb_tracker', 'UserGroupExtension')
    
    # Recreate Manager_lvl1 group
    group1, created = Group.objects.get_or_create(name='Manager_lvl1')
    if created:
        UserGroupExtension.objects.create(
            group=group1,
            level=1,
            department='Management',
            description='Level 1 Manager - Oversees operations and provides final sign-off'
        )
    
    # Recreate Manager_lvl2 group
    group2, created = Group.objects.get_or_create(name='Manager_lvl2')
    if created:
        UserGroupExtension.objects.create(
            group=group2,
            level=2,
            department='Management',
            description='Level 2 Manager - Senior management with additional oversight capabilities'
        )


class Migration(migrations.Migration):

    dependencies = [
        ('pcb_tracker', '0010_add_pcb_manager_group'),
    ]

    operations = [
        migrations.RunPython(remove_old_manager_groups, reverse_remove_old_manager_groups),
    ]