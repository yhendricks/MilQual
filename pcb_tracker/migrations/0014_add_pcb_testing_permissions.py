# Generated migration to add necessary permissions to pcb_testing group
from django.db import migrations

def add_pcb_testing_permissions(apps, schema_editor):
    """Add necessary permissions to pcb_testing group"""
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')
    ContentType = apps.get_model('contenttypes', 'ContentType')
    UserGroupExtension = apps.get_model('pcb_tracker', 'UserGroupExtension')
    
    try:
        # Get the pcb_testing group
        pcb_testing_group, created = Group.objects.get_or_create(name='pcb_testing')
        
        # Get content types for the relevant models
        pcb_content_type = ContentType.objects.get(app_label='pcb_tracker', model='pcb')
        testmeasurement_content_type = ContentType.objects.get(app_label='pcb_tracker', model='testmeasurement')
        parametermeasurement_content_type = ContentType.objects.get(app_label='pcb_tracker', model='parametermeasurement')
        questionresponse_content_type = ContentType.objects.get(app_label='pcb_tracker', model='questionresponse')
        fileattachment_content_type = ContentType.objects.get(app_label='pcb_tracker', model='fileattachment')
        
        # Define the permissions needed for PCB testing
        permissions_to_add = [
            # PCB permissions
            ('add_pcb', pcb_content_type),
            ('view_pcb', pcb_content_type),
            ('change_pcb', pcb_content_type),
            
            # Test measurement permissions
            ('add_testmeasurement', testmeasurement_content_type),
            ('view_testmeasurement', testmeasurement_content_type),
            
            # Parameter measurement permissions
            ('add_parametermeasurement', parametermeasurement_content_type),
            ('view_parametermeasurement', parametermeasurement_content_type),
            
            # Question response permissions
            ('add_questionresponse', questionresponse_content_type),
            ('view_questionresponse', questionresponse_content_type),
            
            # File attachment permissions
            ('add_fileattachment', fileattachment_content_type),
            ('view_fileattachment', fileattachment_content_type),
        ]
        
        # Add each permission to the group
        for codename, content_type in permissions_to_add:
            try:
                permission = Permission.objects.get(content_type=content_type, codename=codename)
                pcb_testing_group.permissions.add(permission)
                print(f"Added permission {codename} to pcb_testing group")
            except Permission.DoesNotExist:
                print(f"Permission {codename} does not exist")
        
        # Create UserGroupExtension if it doesn't exist
        if created:
            UserGroupExtension.objects.create(
                group=pcb_testing_group,
                level=1,
                department='Testing',
                description='PCB Testing - Tests individual PCBs'
            )
            print("Created UserGroupExtension for pcb_testing")
        
        print("Successfully added permissions to pcb_testing group")
        
    except Exception as e:
        print(f"Error adding permissions: {e}")
        raise


def reverse_add_pcb_testing_permissions(apps, schema_editor):
    """Reverse: Remove the added permissions from pcb_testing group"""
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')
    ContentType = apps.get_model('contenttypes', 'ContentType')
    
    try:
        # Get the pcb_testing group
        try:
            pcb_testing_group = Group.objects.get(name='pcb_testing')
        except Group.DoesNotExist:
            print("pcb_testing group does not exist, skipping reverse migration")
            return
        
        # Get content types for the relevant models
        pcb_content_type = ContentType.objects.get(app_label='pcb_tracker', model='pcb')
        testmeasurement_content_type = ContentType.objects.get(app_label='pcb_tracker', model='testmeasurement')
        parametermeasurement_content_type = ContentType.objects.get(app_label='pcb_tracker', model='parametermeasurement')
        questionresponse_content_type = ContentType.objects.get(app_label='pcb_tracker', model='questionresponse')
        fileattachment_content_type = ContentType.objects.get(app_label='pcb_tracker', model='fileattachment')
        
        # Define the permissions that were added
        permissions_to_remove = [
            # PCB permissions
            ('add_pcb', pcb_content_type),
            ('view_pcb', pcb_content_type),
            ('change_pcb', pcb_content_type),
            
            # Test measurement permissions
            ('add_testmeasurement', testmeasurement_content_type),
            ('view_testmeasurement', testmeasurement_content_type),
            
            # Parameter measurement permissions
            ('add_parametermeasurement', parametermeasurement_content_type),
            ('view_parametermeasurement', parametermeasurement_content_type),
            
            # Question response permissions
            ('add_questionresponse', questionresponse_content_type),
            ('view_questionresponse', questionresponse_content_type),
            
            # File attachment permissions
            ('add_fileattachment', fileattachment_content_type),
            ('view_fileattachment', fileattachment_content_type),
        ]
        
        # Remove each permission from the group
        for codename, content_type in permissions_to_remove:
            try:
                permission = Permission.objects.get(content_type=content_type, codename=codename)
                pcb_testing_group.permissions.remove(permission)
                print(f"Removed permission {codename} from pcb_testing group")
            except Permission.DoesNotExist:
                print(f"Permission {codename} does not exist to remove")
        
        print("Successfully removed permissions from pcb_testing group")
        
    except Exception as e:
        print(f"Error removing permissions: {e}")
        raise


class Migration(migrations.Migration):

    dependencies = [
        ('pcb_tracker', '0013_remove_deprecated_groups'),
    ]

    operations = [
        migrations.RunPython(
            add_pcb_testing_permissions,
            reverse_add_pcb_testing_permissions
        ),
    ]