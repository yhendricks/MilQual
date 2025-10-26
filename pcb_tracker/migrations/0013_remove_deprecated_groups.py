# Generated migration to remove users from deprecated groups
from django.db import migrations

def remove_users_from_deprecated_groups(apps, schema_editor):
    """Remove users from deprecated groups"""
    Group = apps.get_model('auth', 'Group')
    User = apps.get_model('auth', 'User')
    
    # List of groups to remove users from (if they exist)
    deprecated_groups = [
        'assembler_lvl1',
        'QA_lvl1', 
        'QA_lvl2',
        'Function_tester_lvl1',
        'Function_tester_lvl2'
    ]
    
    for group_name in deprecated_groups:
        try:
            group = Group.objects.get(name=group_name)
            # Get all users in this group
            group_users = group.user_set.all()
            
            # Remove all users from this group
            for user in group_users:
                user.groups.remove(group)
                print(f"Removed user {user.username} from deprecated group {group_name}")
            
            # Delete the group itself
            group.delete()
            print(f"Deleted deprecated group {group_name}")
            
        except Group.DoesNotExist:
            # Group doesn't exist, which is fine
            print(f"Group {group_name} does not exist, skipping")
            continue


def reverse_remove_users_from_deprecated_groups(apps, schema_editor):
    """Reverse: This is a no-op since we don't want to recreate the groups"""
    print("Reverse migration: No action taken as groups were fully removed")


class Migration(migrations.Migration):

    dependencies = [
        ('pcb_tracker', '0012_migrate_board_tester_to_pcb_testing'),
    ]

    operations = [
        migrations.RunPython(
            remove_users_from_deprecated_groups,
            reverse_remove_users_from_deprecated_groups
        ),
    ]