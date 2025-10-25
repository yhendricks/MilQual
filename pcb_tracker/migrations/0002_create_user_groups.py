from django.db import migrations
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from pcb_tracker.models import UserGroupExtension


def create_user_groups(apps, schema_editor):
    """Create the required user groups with their permissions"""
    
    # Define the groups to create
    groups_config = [
        {'name': 'board_tester_lvl1', 'level': 1, 'department': 'Testing', 'description': 'Level 1 Board Tester - Tests individual PCBs'},
        {'name': 'board_tester_lvl2', 'level': 2, 'department': 'Testing', 'description': 'Level 2 Board Tester - Tests individual PCBs with advanced capabilities'},
        {'name': 'assembler_lvl1', 'level': 1, 'department': 'Assembly', 'description': 'Level 1 Assembler - Assembles PCBs into modules'},
        {'name': 'QA_lvl1', 'level': 1, 'department': 'Quality Assurance', 'description': 'Level 1 Quality Assurance - Verifies test results and approves for next stage'},
        {'name': 'QA_lvl2', 'level': 2, 'department': 'Quality Assurance', 'description': 'Level 2 Quality Assurance - Advanced QA with additional permissions'},
        {'name': 'Function_tester_lvl1', 'level': 1, 'department': 'Testing', 'description': 'Level 1 Functional Tester - Tests modules for functionality'},
        {'name': 'Function_tester_lvl2', 'level': 2, 'department': 'Testing', 'description': 'Level 2 Functional Tester - Advanced functional testing'},
        {'name': 'Environmental_tester_lvl1', 'level': 1, 'department': 'Testing', 'description': 'Level 1 Environmental Tester - Performs environmental testing on modules'},
        {'name': 'Manager_lvl1', 'level': 1, 'department': 'Management', 'description': 'Level 1 Manager - Oversees operations and provides final sign-off'},
        {'name': 'Manager_lvl2', 'level': 2, 'department': 'Management', 'description': 'Level 2 Manager - Senior management with additional oversight capabilities'},
        {'name': 'test_config_manager', 'level': 2, 'department': 'Engineering', 'description': 'Test Configuration Manager - Manages test configurations and parameters'},
        {'name': 'Admin', 'level': 99, 'department': 'Administration', 'description': 'System Administrator with full access'},
    ]
    
    # Create groups and their extensions
    for config in groups_config:
        group, created = Group.objects.get_or_create(name=config['name'])
        if created:
            extension = UserGroupExtension.objects.create(
                group=group,
                level=config['level'],
                department=config['department'],
                description=config['description']
            )
    
    # Define permissions for each group
    pcb_content_type = ContentType.objects.get_for_model(apps.get_model('pcb_tracker', 'PCB'))
    batch_content_type = ContentType.objects.get_for_model(apps.get_model('pcb_tracker', 'Batch'))
    pcb_type_content_type = ContentType.objects.get_for_model(apps.get_model('pcb_tracker', 'PCBType'))
    test_measurement_content_type = ContentType.objects.get_for_model(apps.get_model('pcb_tracker', 'TestMeasurement'))
    module_content_type = ContentType.objects.get_for_model(apps.get_model('pcb_tracker', 'Module'))
    module_test_record_content_type = ContentType.objects.get_for_model(apps.get_model('pcb_tracker', 'ModuleTestRecord'))
    file_attachment_content_type = ContentType.objects.get_for_model(apps.get_model('pcb_tracker', 'FileAttachment'))
    
    # Test config content types (if they exist in this migration)
    try:
        test_config_content_type = ContentType.objects.get_for_model(apps.get_model('pcb_tracker', 'TestConfig'))
        test_parameter_content_type = ContentType.objects.get_for_model(apps.get_model('pcb_tracker', 'TestParameter'))
        test_question_content_type = ContentType.objects.get_for_model(apps.get_model('pcb_tracker', 'TestQuestion'))
    except:
        # If models don't exist yet in this migration, we'll add permissions later
        test_config_content_type = None
        test_parameter_content_type = None
        test_question_content_type = None
    
    permissions_config = {
        'board_tester_lvl1': [
            # Can add and view PCBs
            {'codename': 'add_pcb', 'content_type': pcb_content_type},
            {'codename': 'view_pcb', 'content_type': pcb_content_type},
            
            # Can add and view test measurements
            {'codename': 'add_testmeasurement', 'content_type': test_measurement_content_type},
            {'codename': 'view_testmeasurement', 'content_type': test_measurement_content_type},
            
            # Can add and view file attachments
            {'codename': 'add_fileattachment', 'content_type': file_attachment_content_type},
            {'codename': 'view_fileattachment', 'content_type': file_attachment_content_type},
        ],
        
        'Manager_lvl1': [
            # Can view everything
            {'codename': 'add_pcbtype', 'content_type': pcb_type_content_type},
            {'codename': 'view_pcbtype', 'content_type': pcb_type_content_type},
            {'codename': 'change_pcbtype', 'content_type': pcb_type_content_type},
            {'codename': 'delete_pcbtype', 'content_type': pcb_type_content_type},
            
            {'codename': 'view_pcb', 'content_type': pcb_content_type},
            {'codename': 'view_batch', 'content_type': batch_content_type},
            {'codename': 'view_testmeasurement', 'content_type': test_measurement_content_type},
            {'codename': 'view_module', 'content_type': module_content_type},
            {'codename': 'view_moduletestrecord', 'content_type': module_test_record_content_type},
            {'codename': 'view_fileattachment', 'content_type': file_attachment_content_type},
        ],
        
        'board_tester_lvl2': [
            # Same as lvl1 but with additional permissions
            {'codename': 'add_pcb', 'content_type': pcb_content_type},
            {'codename': 'view_pcb', 'content_type': pcb_content_type},
            {'codename': 'change_pcb', 'content_type': pcb_content_type},
            
            {'codename': 'add_testmeasurement', 'content_type': test_measurement_content_type},
            {'codename': 'view_testmeasurement', 'content_type': test_measurement_content_type},
            {'codename': 'change_testmeasurement', 'content_type': test_measurement_content_type},
            
            {'codename': 'add_fileattachment', 'content_type': file_attachment_content_type},
            {'codename': 'view_fileattachment', 'content_type': file_attachment_content_type},
        ],
        
        'assembler_lvl1': [
            # Can view PCBs (only approved ones)
            {'codename': 'view_pcb', 'content_type': pcb_content_type},
            
            # Can create and view modules
            {'codename': 'add_module', 'content_type': module_content_type},
            {'codename': 'view_module', 'content_type': module_content_type},
        ],
        
        'QA_lvl1': [
            # Can view PCBs and change status
            {'codename': 'view_pcb', 'content_type': pcb_content_type},
            {'codename': 'change_pcb', 'content_type': pcb_content_type},
            
            # Can view test measurements
            {'codename': 'view_testmeasurement', 'content_type': test_measurement_content_type},
            
            # Can view and add file attachments
            {'codename': 'view_fileattachment', 'content_type': file_attachment_content_type},
            {'codename': 'add_fileattachment', 'content_type': file_attachment_content_type},
        ],
        
        'QA_lvl2': [
            # Same as QA_lvl1 but with additional permissions
            {'codename': 'add_pcb', 'content_type': pcb_content_type},
            {'codename': 'view_pcb', 'content_type': pcb_content_type},
            {'codename': 'change_pcb', 'content_type': pcb_content_type},
            {'codename': 'delete_pcb', 'content_type': pcb_content_type},
            
            {'codename': 'add_testmeasurement', 'content_type': test_measurement_content_type},
            {'codename': 'view_testmeasurement', 'content_type': test_measurement_content_type},
            {'codename': 'change_testmeasurement', 'content_type': test_measurement_content_type},
            {'codename': 'delete_testmeasurement', 'content_type': test_measurement_content_type},
            
            {'codename': 'add_fileattachment', 'content_type': file_attachment_content_type},
            {'codename': 'view_fileattachment', 'content_type': file_attachment_content_type},
            {'codename': 'delete_fileattachment', 'content_type': file_attachment_content_type},
            
            {'codename': 'add_module', 'content_type': module_content_type},
            {'codename': 'view_module', 'content_type': module_content_type},
            {'codename': 'change_module', 'content_type': module_content_type},
        ],
        
        'Manager_lvl2': [
            # Can view and change everything including PCB types
            {'codename': 'add_pcbtype', 'content_type': pcb_type_content_type},
            {'codename': 'view_pcbtype', 'content_type': pcb_type_content_type},
            {'codename': 'change_pcbtype', 'content_type': pcb_type_content_type},
            {'codename': 'delete_pcbtype', 'content_type': pcb_type_content_type},
            
            {'codename': 'view_pcb', 'content_type': pcb_content_type},
            {'codename': 'change_pcb', 'content_type': pcb_content_type},
            {'codename': 'view_batch', 'content_type': batch_content_type},
            {'codename': 'view_testmeasurement', 'content_type': test_measurement_content_type},
            {'codename': 'view_module', 'content_type': module_content_type},
            {'codename': 'change_module', 'content_type': module_content_type},
            {'codename': 'view_moduletestrecord', 'content_type': module_test_record_content_type},
            {'codename': 'view_fileattachment', 'content_type': file_attachment_content_type},
        ],
        
        'Function_tester_lvl1': [
            # Can view modules
            {'codename': 'view_module', 'content_type': module_content_type},
            
            # Can create and view module test records
            {'codename': 'add_moduletestrecord', 'content_type': module_test_record_content_type},
            {'codename': 'view_moduletestrecord', 'content_type': module_test_record_content_type},
            
            # Can add and view file attachments
            {'codename': 'add_fileattachment', 'content_type': file_attachment_content_type},
            {'codename': 'view_fileattachment', 'content_type': file_attachment_content_type},
        ],
        
        'Function_tester_lvl2': [
            # Same as lvl1 with additional permissions
            {'codename': 'view_module', 'content_type': module_content_type},
            {'codename': 'change_module', 'content_type': module_content_type},
            
            {'codename': 'add_moduletestrecord', 'content_type': module_test_record_content_type},
            {'codename': 'view_moduletestrecord', 'content_type': module_test_record_content_type},
            {'codename': 'change_moduletestrecord', 'content_type': module_test_record_content_type},
            
            {'codename': 'add_fileattachment', 'content_type': file_attachment_content_type},
            {'codename': 'view_fileattachment', 'content_type': file_attachment_content_type},
        ],
        
        'Environmental_tester_lvl1': [
            # Can view modules
            {'codename': 'view_module', 'content_type': module_content_type},
            
            # Can create and view module test records
            {'codename': 'add_moduletestrecord', 'content_type': module_test_record_content_type},
            {'codename': 'view_moduletestrecord', 'content_type': module_test_record_content_type},
            
            # Can add and view file attachments
            {'codename': 'add_fileattachment', 'content_type': file_attachment_content_type},
            {'codename': 'view_fileattachment', 'content_type': file_attachment_content_type},
        ],
        
        'Manager_lvl1': [
            # Can view everything
            {'codename': 'view_pcb', 'content_type': pcb_content_type},
            {'codename': 'view_batch', 'content_type': batch_content_type},
            {'codename': 'view_testmeasurement', 'content_type': test_measurement_content_type},
            {'codename': 'view_module', 'content_type': module_content_type},
            {'codename': 'view_moduletestrecord', 'content_type': module_test_record_content_type},
            {'codename': 'view_fileattachment', 'content_type': file_attachment_content_type},
        ],
        
        'Manager_lvl2': [
            # Can view and change everything
            {'codename': 'view_pcb', 'content_type': pcb_content_type},
            {'codename': 'change_pcb', 'content_type': pcb_content_type},
            {'codename': 'view_batch', 'content_type': batch_content_type},
            {'codename': 'view_testmeasurement', 'content_type': test_measurement_content_type},
            {'codename': 'view_module', 'content_type': module_content_type},
            {'codename': 'change_module', 'content_type': module_content_type},
            {'codename': 'view_moduletestrecord', 'content_type': module_test_record_content_type},
            {'codename': 'view_fileattachment', 'content_type': file_attachment_content_type},
        ],
        
        'Admin': [
            # All permissions including PCB types
            {'codename': 'add_pcbtype', 'content_type': pcb_type_content_type},
            {'codename': 'view_pcbtype', 'content_type': pcb_type_content_type},
            {'codename': 'change_pcbtype', 'content_type': pcb_type_content_type},
            {'codename': 'delete_pcbtype', 'content_type': pcb_type_content_type},
            
            {'codename': 'add_pcb', 'content_type': pcb_content_type},
            {'codename': 'view_pcb', 'content_type': pcb_content_type},
            {'codename': 'change_pcb', 'content_type': pcb_content_type},
            {'codename': 'delete_pcb', 'content_type': pcb_content_type},
            
            {'codename': 'add_batch', 'content_type': batch_content_type},
            {'codename': 'view_batch', 'content_type': batch_content_type},
            {'codename': 'change_batch', 'content_type': batch_content_type},
            {'codename': 'delete_batch', 'content_type': batch_content_type},
            
            {'codename': 'add_testmeasurement', 'content_type': test_measurement_content_type},
            {'codename': 'view_testmeasurement', 'content_type': test_measurement_content_type},
            {'codename': 'change_testmeasurement', 'content_type': test_measurement_content_type},
            {'codename': 'delete_testmeasurement', 'content_type': test_measurement_content_type},
            
            {'codename': 'add_module', 'content_type': module_content_type},
            {'codename': 'view_module', 'content_type': module_content_type},
            {'codename': 'change_module', 'content_type': module_content_type},
            {'codename': 'delete_module', 'content_type': module_content_type},
            
            {'codename': 'add_moduletestrecord', 'content_type': module_test_record_content_type},
            {'codename': 'view_moduletestrecord', 'content_type': module_test_record_content_type},
            {'codename': 'change_moduletestrecord', 'content_type': module_test_record_content_type},
            {'codename': 'delete_moduletestrecord', 'content_type': module_test_record_content_type},
            
            {'codename': 'add_fileattachment', 'content_type': file_attachment_content_type},
            {'codename': 'view_fileattachment', 'content_type': file_attachment_content_type},
            {'codename': 'change_fileattachment', 'content_type': file_attachment_content_type},
            {'codename': 'delete_fileattachment', 'content_type': file_attachment_content_type},
        ],
        
        'test_config_manager': [
            # Full CRUD permissions for test configurations
            {'codename': 'add_testconfig', 'content_type': test_config_content_type},
            {'codename': 'view_testconfig', 'content_type': test_config_content_type},
            {'codename': 'change_testconfig', 'content_type': test_config_content_type},
            {'codename': 'delete_testconfig', 'content_type': test_config_content_type},
            {'codename': 'add_testparameter', 'content_type': test_parameter_content_type},
            {'codename': 'view_testparameter', 'content_type': test_parameter_content_type},
            {'codename': 'change_testparameter', 'content_type': test_parameter_content_type},
            {'codename': 'delete_testparameter', 'content_type': test_parameter_content_type},
            {'codename': 'add_testquestion', 'content_type': test_question_content_type},
            {'codename': 'view_testquestion', 'content_type': test_question_content_type},
            {'codename': 'change_testquestion', 'content_type': test_question_content_type},
            {'codename': 'delete_testquestion', 'content_type': test_question_content_type},
            
            # Can also view related models
            {'codename': 'view_pcbtype', 'content_type': pcb_type_content_type},
            {'codename': 'view_pcb', 'content_type': pcb_content_type},
        ],
    }
    
    # Assign permissions to each group
    for group_name, perms in permissions_config.items():
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


def reverse_create_user_groups(apps, schema_editor):
    """Reverse the group creation"""
    Group = apps.get_model('auth', 'Group')
    UserGroupExtension = apps.get_model('pcb_tracker', 'UserGroupExtension')
    
    # Delete the groups we created
    group_names = [
        'board_tester_lvl1', 'board_tester_lvl2', 'assembler_lvl1',
        'QA_lvl1', 'QA_lvl2', 'Function_tester_lvl1', 'Function_tester_lvl2',
        'Environmental_tester_lvl1', 'Manager_lvl1', 'Manager_lvl2', 'Admin'
    ]
    
    for name in group_names:
        try:
            UserGroupExtension.objects.get(group__name=name).delete()
            Group.objects.get(name=name).delete()
        except:
            pass  # Group doesn't exist, continue


class Migration(migrations.Migration):

    dependencies = [
        ('pcb_tracker', '0001_initial'),
        ('auth', '0012_alter_user_first_name_max_length'),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.RunPython(create_user_groups, reverse_create_user_groups),
    ]