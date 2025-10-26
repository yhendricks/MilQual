# Generated migration to move users from board_tester_lvl1 to pcb_testing group
from django.db import migrations

def migrate_board_tester_to_pcb_testing(apps, schema_editor):
    """Move users from board_tester_lvl1 group to pcb_testing group"""
    Group = apps.get_model('auth', 'Group')
    User = apps.get_model('auth', 'User')
    
    try:
        # Get the old group (if it exists)
        try:
            old_group = Group.objects.get(name='board_tester_lvl1')
        except Group.DoesNotExist:
            # If the old group doesn't exist, nothing to migrate
            print("board_tester_lvl1 group does not exist, skipping migration")
            return
        
        # Get or create the new group
        new_group, created = Group.objects.get_or_create(
            name='pcb_testing',
            defaults={
                'name': 'pcb_testing'
            }
        )
        
        # Get all users in the old group
        old_group_users = old_group.user_set.all()
        
        # Add these users to the new group
        for user in old_group_users:
            if new_group not in user.groups.all():
                user.groups.add(new_group)
                print(f"Added user {user.username} to pcb_testing group")
        
        # Remove users from the old group (or delete the old group entirely)
        for user in old_group_users:
            user.groups.remove(old_group)
        
        # Optionally delete the old group after moving users
        old_group.delete()
        print("Migrated users from board_tester_lvl1 to pcb_testing and deleted old group")
        
    except Exception as e:
        print(f"Error during migration: {e}")
        raise


def reverse_migrate_pcb_testing_to_board_tester(apps, schema_editor):
    """Reverse: move users from pcb_testing back to board_tester_lvl1"""
    Group = apps.get_model('auth', 'Group')
    User = apps.get_model('auth', 'User')
    
    try:
        # Get the new group (if it exists)
        try:
            new_group = Group.objects.get(name='pcb_testing')
        except Group.DoesNotExist:
            # If the new group doesn't exist, nothing to reverse
            print("pcb_testing group does not exist, skipping reverse migration")
            return
        
        # Get or create the old group
        old_group, created = Group.objects.get_or_create(
            name='board_tester_lvl1',
            defaults={
                'name': 'board_tester_lvl1'
            }
        )
        
        # Get all users in the new group
        new_group_users = new_group.user_set.all()
        
        # Add these users to the old group
        for user in new_group_users:
            if old_group not in user.groups.all():
                user.groups.add(old_group)
                print(f"Added user {user.username} back to board_tester_lvl1 group")
        
        # Remove users from the new group
        for user in new_group_users:
            user.groups.remove(new_group)
        
        # Delete the new group
        new_group.delete()
        print("Reversed migration: moved users back to board_tester_lvl1 from pcb_testing and deleted new group")
        
    except Exception as e:
        print(f"Error during reverse migration: {e}")
        raise


class Migration(migrations.Migration):

    dependencies = [
        ('pcb_tracker', '0011_remove_old_manager_groups'),
    ]

    operations = [
        migrations.RunPython(
            migrate_board_tester_to_pcb_testing,
            reverse_migrate_pcb_testing_to_board_tester
        ),
    ]