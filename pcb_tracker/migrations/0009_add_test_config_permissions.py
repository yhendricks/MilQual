from django.db import migrations
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType


def add_test_config_permissions(apps, schema_editor):
    """Add permissions for test configuration management"""
    
    # Get content types for the new models
    try:
        TestConfig = apps.get_model('pcb_tracker', 'TestConfig')
        TestParameter = apps.get_model('pcb_tracker', 'TestParameter')
        TestQuestion = apps.get_model('pcb_tracker', 'TestQuestion')
        
        test_config_content_type = ContentType.objects.get_for_model(TestConfig)
        test_parameter_content_type = ContentType.objects.get_for_model(TestParameter)
        test_question_content_type = ContentType.objects.get_for_model(TestQuestion)
    except LookupError:
        # Models don't exist yet, skip
        return
    
    # Get or create the test_config_manager group
    group, created = Group.objects.get_or_create(name='test_config_manager')
    
    # Define permissions for test config management
    permissions = [
        # TestConfig permissions
        {'codename': 'add_testconfig', 'content_type': test_config_content_type},
        {'codename': 'view_testconfig', 'content_type': test_config_content_type},
        {'codename': 'change_testconfig', 'content_type': test_config_content_type},
        {'codename': 'delete_testconfig', 'content_type': test_config_content_type},
        
        # TestParameter permissions
        {'codename': 'add_testparameter', 'content_type': test_parameter_content_type},
        {'codename': 'view_testparameter', 'content_type': test_parameter_content_type},
        {'codename': 'change_testparameter', 'content_type': test_parameter_content_type},
        {'codename': 'delete_testparameter', 'content_type': test_parameter_content_type},
        
        # TestQuestion permissions
        {'codename': 'add_testquestion', 'content_type': test_question_content_type},
        {'codename': 'view_testquestion', 'content_type': test_question_content_type},
        {'codename': 'change_testquestion', 'content_type': test_question_content_type},
        {'codename': 'delete_testquestion', 'content_type': test_question_content_type},
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


def reverse_add_test_config_permissions(apps, schema_editor):
    """Reverse the permission additions"""
    try:
        group = Group.objects.get(name='test_config_manager')
        group.delete()
    except Group.DoesNotExist:
        pass


class Migration(migrations.Migration):

    dependencies = [
        ('pcb_tracker', '0008_testconfig_pcb_test_config_and_more'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.RunPython(add_test_config_permissions, reverse_add_test_config_permissions),
    ]