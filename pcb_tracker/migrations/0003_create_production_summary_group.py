from django.db import migrations
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType


def create_production_summary_group(apps, schema_editor):
    """Create a group specifically for production summary access"""
    Group = apps.get_model('auth', 'Group')
    UserGroupExtension = apps.get_model('pcb_tracker', 'UserGroupExtension')
    
    # Create the production_summary group
    group, created = Group.objects.get_or_create(name='production_summary')
    
    if created:
        # Create extension for the group
        extension = UserGroupExtension.objects.create(
            group=group,
            level=0,  # Default level
            department='Production',
            description='Group that can view production summary'
        )


def reverse_create_production_summary_group(apps, schema_editor):
    """Reverse the group creation"""
    Group = apps.get_model('auth', 'Group')
    UserGroupExtension = apps.get_model('pcb_tracker', 'UserGroupExtension')
    
    try:
        extension = UserGroupExtension.objects.get(group__name='production_summary')
        extension.delete()
        Group.objects.get(name='production_summary').delete()
    except:
        pass  # Group doesn't exist, continue


class Migration(migrations.Migration):

    dependencies = [
        ('pcb_tracker', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_production_summary_group, reverse_create_production_summary_group),
    ]